#!/usr/bin/env python3
import asyncio
import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import aiohttp
import pandas as pd
from core.settings import Settings
from core.data_base import init_database


class CEPProcessor:
    """Processador simplificado de CEPs com consultas paralelas"""
    
    def __init__(self):
        """
        Inicializa o processador
        
        Args:
            settings: Objeto Settings com configurações
        """
        self.settings = Settings
        self.results = []
        self.errors = []
        self.stats = {
            'total': 0,
            'success': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        init_database()
    
    async def fetch_cep_with_retry(
        self, 
        cep: str, 
        session: aiohttp.ClientSession
    ) -> Optional[Dict]:
        """
        Consulta um CEP com retry automático
        
        Args:
            cep: CEP a ser consultado
            session: Sessão aiohttp compartilhada
            
        Returns:
            Dados do CEP ou None em caso de erro
        """
        url = self.settings.SERVICE_CEP.format(cep=cep)
        
        for attempt in range(self.settings.MAX_RETRIES):
            try:
                async with session.get(url, timeout=self.settings.REQUEST_TIMEOUT) as resp:
                    
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # ViaCEP retorna {"erro": true} para CEPs inválidos
                        if isinstance(data, dict) and data.get('erro'):
                            self.errors.append({
                                'cep': cep,
                                'error': 'CEP não encontrado na base ViaCEP',
                                'timestamp': datetime.now().isoformat()
                            })
                            self.stats['errors'] += 1
                            return None
                        
                        # Sucesso
                        self.stats['success'] += 1
                        return data
                    
                    else:
                        # HTTP error
                        if attempt == self.settings.MAX_RETRIES - 1:
                            self.errors.append({
                                'cep': cep,
                                'error': f'HTTP {resp.status}',
                                'timestamp': datetime.now().isoformat()
                            })
                            self.stats['errors'] += 1
                        else:
                            # Backoff exponencial
                            await asyncio.sleep(0.5 * (attempt + 1))
            
            except asyncio.TimeoutError:
                if attempt == self.settings.MAX_RETRIES - 1:
                    self.errors.append({
                        'cep': cep,
                        'error': 'Timeout na requisição',
                        'timestamp': datetime.now().isoformat()
                    })
                    self.stats['errors'] += 1
                else:
                    await asyncio.sleep(0.5 * (attempt + 1))
            
            except Exception as e:
                if attempt == self.settings.MAX_RETRIES - 1:
                    self.errors.append({
                        'cep': cep,
                        'error': f'Erro: {str(e)}',
                        'timestamp': datetime.now().isoformat()
                    })
                    self.stats['errors'] += 1
                else:
                    await asyncio.sleep(0.5 * (attempt + 1))
        
        return None
    
    async def process_batch_async(
        self, 
        ceps_list: List[str], 
        session: aiohttp.ClientSession
    ):
        """
        Processa um lote de CEPs em paralelo
        Simplificado: remove items da lista conforme processa
        
        Args:
            ceps_list: Lista de CEPs (será modificada - items removidos)
            session: Sessão aiohttp compartilhada
        """
        batch_results = []
        
        while ceps_list:
            # Pega até MAX_CONCURRENT_REQUESTS CEPs da lista e remove
            batch = [
                ceps_list.pop(0) 
                for _ in range(min(self.settings.MAX_CONCURRENT_REQUESTS, len(ceps_list)))
            ]
            
            # Cria tasks para processar em paralelo
            tasks = [
                self.fetch_cep_with_retry(cep, session) 
                for cep in batch
            ]
            
            # Aguarda todas as tasks do batch
            results = await asyncio.gather(*tasks)
            
            # Filtra resultados válidos
            for result in results:
                if result:
                    batch_results.append(result)
        
        return batch_results
    
    async def process(self, ceps: List[str]):
        """
        Processa todos os CEPs com session única
        
        Args:
            ceps: Lista de CEPs para processar
        """
        self.stats['total'] = len(ceps)
        self.stats['start_time'] = time.time()
        
        print(f"\n{'='*60}")
        print(f"Processando {len(ceps)} CEPs...")
        print(f"Requisições simultâneas: {self.settings.MAX_CONCURRENT_REQUESTS}")
        print(f"Timeout: {self.settings.REQUEST_TIMEOUT}s")
        print(f"Max retries: {self.settings.MAX_RETRIES}")
        print(f"{'='*60}\n")
        
        # Cria cópia da lista para não modificar a original
        ceps_to_process = ceps.copy()
        total_ceps = len(ceps_to_process)
        
        # Session única para todas as requisições
        connector = aiohttp.TCPConnector(limit=self.settings.MAX_CONCURRENT_REQUESTS * 2)
        timeout = aiohttp.ClientTimeout(total=self.settings.REQUEST_TIMEOUT)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            
            # Processa em chunks de 100 para dar feedback
            chunk_size = 100
            while ceps_to_process:
                # Pega próximo chunk
                chunk = ceps_to_process[:chunk_size]
                chunk_copy = chunk.copy()
                
                # Remove chunk da lista principal
                ceps_to_process = ceps_to_process[chunk_size:]
                
                # Processa chunk
                chunk_results = await self.process_batch_async(chunk_copy, session)
                self.results.extend(chunk_results)
                
                # Feedback de progresso
                processed = total_ceps - len(ceps_to_process)
                print(f"Processados: {processed}/{total_ceps} CEPs")
        
        self.stats['end_time'] = time.time()
        
        # Salva todos os outputs
        self.save_to_database()
        self.save_errors_csv()
        self.save_json()
        self.save_xml()
        
        self.print_stats()
    
    def save_to_database(self):
        """Salva resultados no SQLite"""
        if not self.results:
            print("Nenhum resultado para salvar no banco")
            return
        
        conn = sqlite3.connect(self.settings.DB_PATH)
        cursor = conn.cursor()
        
        inserted = 0
        updated = 0
        
        for data in self.results:
            try:
                cep = data.get('cep')
                
                # Verifica se já existe
                cursor.execute('SELECT id FROM results WHERE cep = ?', (cep,))
                exists = cursor.fetchone()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO results (cep, data)
                    VALUES (?, ?)
                ''', (cep, json.dumps(data, ensure_ascii=False)))
                
                if exists:
                    updated += 1
                else:
                    inserted += 1
                    
            except Exception as e:
                print(f"Erro ao salvar CEP {data.get('cep')}: {e}")
        
        # Salva erros
        for error in self.errors:
            try:
                cursor.execute('''
                    INSERT INTO errors (cep, error_message)
                    VALUES (?, ?)
                ''', (error['cep'], error['error']))
            except Exception as e:
                print(f"Erro ao salvar log de erro: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"Banco de dados: {inserted} novos, {updated} atualizados")
    
    def save_errors_csv(self):
        """Salva erros em CSV"""
        if not self.errors:
            print("Nenhum erro para registrar")
            return
        
        df_errors = pd.DataFrame(self.errors)
        df_errors.to_csv(self.settings.CSV_ERRORS, index=False, encoding='utf-8')
        print(f"Erros salvos: {self.settings.CSV_ERRORS} ({len(self.errors)} registros)")
    
    def save_json(self):
        """Salva resultados em JSON"""
        with open(self.settings.JSON_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"JSON salvo: {self.settings.JSON_OUTPUT}")
    
    def save_xml(self):
        """Salva resultados em XML"""
        root = Element('enderecos')
        
        for data in self.results:
            endereco = SubElement(root, 'endereco')
            for key, value in data.items():
                child = SubElement(endereco, key)
                child.text = str(value) if value else ''
        
        # Pretty print
        xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        
        with open(self.settings.XML_OUTPUT, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        print(f"XML salvo: {self.settings.XML_OUTPUT}")
    
    def print_stats(self):
        """Imprime estatísticas do processamento"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        print(f"\n{'='*60}")
        print(f"📊 ESTATÍSTICAS DO PROCESSAMENTO")
        print(f"{'='*60}")
        print(f"Total de CEPs:     {self.stats['total']:,}")
        print(f"Sucessos:        {self.stats['success']:,}")
        print(f"Erros:           {self.stats['errors']:,}")
        print(f"Taxa de sucesso:   {(self.stats['success']/self.stats['total']*100):.2f}%")
        print(f"Tempo total:       {duration:.2f}s ({duration/60:.1f} min)")
        print(f"Velocidade:        {(self.stats['total']/duration):.2f} CEPs/segundo")
        print(f"{'='*60}\n")
