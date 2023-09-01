import json
import sqlalchemy
import cx_Oracle

from sqlalchemy import Column, Integer, String, Identity, LargeBinary, ForeignKey, DECIMAL
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import func, exists
from sqlalchemy.sql import select
from datetime import datetime
from decimal import Decimal
from sqlalchemy.exc import IntegrityError


with open("./db_oracle.json", "r") as file:
    db_variables = json.load(file)

cx_Oracle.init_oracle_client(db_variables["oracle_client_path"])
username = db_variables["username"]
password = db_variables["password"]
server = db_variables["server"]
port = db_variables["port"]
dbname = db_variables["dbname"]

engine = sqlalchemy.create_engine(f"oracle+cx_oracle://{username}:{password}@{server}:{port}/{dbname}?encoding=UTF-8&nencoding=UTF-8")

# Cria uma sessão com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

# Cria uma classe para representar uma tabela no banco de dados
Base = sqlalchemy.orm.declarative_base()

class Login(Base):
    __tablename__ = 'login'
    
    email = Column(String(100), nullable=False, primary_key=True)
    senha = Column(String(50), nullable=False)
    
class Agricultores(Base):
    __tablename__ = 'agricultores'
    
    id_agricultor = Column(Integer, nullable=False, primary_key=True)
    nome_completo = Column(String(100), nullable=False)
    senha = Column(String(100), nullable=False)
    confirmar_senha = Column(String(50), nullable=False)
    cep = Column(String(100), nullable=False)
    logradouro = Column(String(255), nullable=False)
    complemento = Column(String(255))
    localidade = Column(String(255), nullable=False)
    bairro = Column(String(255), nullable=False)
    uf = Column(String(2), nullable=False)
    #Relacionamentos
    email = Column(String(100), ForeignKey('login.email'), nullable=False)
    login = relationship('Login')
    
    @staticmethod
    def next_id(session):
        last_id = session.query(func.max(Agricultores.id_agricultor)).scalar()
        if last_id is not None:
            return last_id + 1
        return 1
    
class Fazenda(Base):
    __tablename__ = 'fazenda'
    
    id_fazenda = Column(Integer, nullable=False, primary_key=True)
    nome_fazenda = Column(String(100), nullable=False)
    localizacao_fazenda = Column(String(100), nullable=False)
    
    #Relacionamentos
    id_agricultor = Column(Integer, ForeignKey('agricultores.id_agricultor'), nullable=False)
    agricultores = relationship('Agricultores')
    
    @staticmethod
    def next_id(session):
        last_id = session.query(func.max(Fazenda.id_fazenda)).scalar()
        if last_id is not None:
            return last_id + 1
        return 1
    
class Vendas(Base):
    __tablename__ = 'vendas'
    
    id_venda = Column(Integer, nullable=False, primary_key=True)
    data_venda = Column(String(10), nullable=False)
    qtd_vendida = Column(Integer, nullable=False)
    preco_venda = Column(DECIMAL(precision=10, scale=2), nullable=False)
    
    id_fazenda = Column(Integer, ForeignKey('fazenda.id_fazenda'), nullable=False)
    fazenda = relationship('Fazenda')
    
    @staticmethod
    def next_id(session):
        last_id = session.query(func.max(Vendas.id_venda)).scalar()
        if last_id is not None:
            return last_id + 1
        return 1
    
class Funcionarios(Base):
    __tablename__ = 'funcionarios'
    
    id_funcionario = Column(Integer, nullable=False, primary_key=True)
    nome_completo = Column(String(100), nullable=False)
    cargo = Column(String(100), nullable=False)
    salario = Column(DECIMAL(precision=10, scale=2), nullable=False)
    
    #relacionamento
    id_fazenda = Column(Integer, ForeignKey('fazenda.id_fazenda'), nullable=False)
    fazenda = relationship('Fazenda')
    
    @staticmethod
    def next_id(session):
        last_id = session.query(func.max(Funcionarios.id_funcionario)).scalar()
        if last_id is not None:
            return last_id + 1
        return 1
    
class Pragas(Base):
    __tablename__ = 'pragas'
    
    id_pragas = Column(Integer, nullable=False, primary_key=True)
    nome_praga = Column(String(100), nullable=False)
    metodo_controle_praga = Column(String(100), nullable=False)
    
    id_fazenda = Column(Integer, ForeignKey('fazenda.id_fazenda'), nullable=False)
    fazenda = relationship('Fazenda')
    
    @staticmethod
    def next_id(session):
        last_id = session.query(func.max(Pragas.id_pragas)).scalar()
        if last_id is not None:
            return last_id + 1
        return 1
    
class Colheitas(Base):
    __tablename__ = 'colheitas'
    
    id_colheita = Column(Integer, nullable=False, primary_key=True)
    tipo_cultura = Column(String(100), nullable=False)
    data_plantio = Column(String(10), nullable=False)
    data_colheita = Column(String(10), nullable=False)
    data_fornecida = Column(String(10), nullable=False)
    qtd_colhida = Column(Integer, nullable=False)
    
    id_fazenda = Column(Integer, ForeignKey('fazenda.id_fazenda'), nullable=False)
    fazenda = relationship('Fazenda')
    
    @staticmethod
    def next_id(session):
        last_id = session.query(func.max(Colheitas.id_colheita)).scalar()
        if last_id is not None:
            return last_id + 1
        return 1

class Insumos(Base):
    __tablename__ = 'insumos'
    
    id_insumo = Column(Integer, nullable=False, primary_key=True)
    nome_insumo = Column(String(100), nullable=False)
    descricao_insumo = Column(String(100), nullable=False)
    fornecedor_insumo = Column(String(100), nullable=False)
    preco_insumo = Column(DECIMAL(precision=10, scale=2), nullable=False)
    
    @staticmethod
    def next_id(session):
        last_id = session.query(func.max(Insumos.id_insumo)).scalar()
        if last_id is not None:
            return last_id + 1
        return 1

class Fornecimentos(Base):
    __tablename__ = 'fornecimentos'
    
    id_fornecimento = Column(Integer, nullable=False, primary_key=True)
    qtd_fornecida = Column(Integer, nullable=False)
    data_fornecimento = Column(String(10), nullable=False)
    
    
    id_fazenda = Column(Integer, ForeignKey('fazenda.id_fazenda'), nullable=False)
    fazenda = relationship('Fazenda')
    
    id_insumo = Column(Integer, ForeignKey('insumos.id_insumo'), nullable=False)
    insumos = relationship('Insumos')
    
    @staticmethod
    def next_id(session):
        last_id = session.query(func.max(Fornecimentos.id_fornecimento)).scalar()
        if last_id is not None:
            return last_id + 1
        return 1
    
Base.metadata.create_all(engine)

try:
    with engine.connect() as connection:
        print("Banco de Dados Conectado")
except sqlalchemy.exc.DatabaseError as e:
    print("Erro ao conectar com o banco: {str(e)}")
    
class Cadastro:
    email_login = None
    @staticmethod
    def inserir_login(session):
        
        try:        
            while True:         
                email = input('Digite seu e-mail: ').upper()
                confirma_email = input('Confirme seu e-mail: ').upper()  
                if email == confirma_email:
                    break
                else:
                    print('Os emails nao conferem, favor verificar')
            
            senha = input('Digite uma senha: ')
            confirme_senha = input('Confirme a senha: ')
            
            while senha != confirme_senha or len(senha) > 50:
                if len(senha) > 50:
                    print('Sua senha possui mais de 50 caracteres, favor corrigir')
                else:
                    print('Suas senhas digitadas não conferem, favor corrigir')
                    
                    senha = input('Digite uma senha (maximo 50 caracteres): ')
                    confirme_senha = input('Confirme sua senha: ')
            
            login = Login(
                email = email,
                senha = senha   
            )
            
            session.add(login)
            
            session.commit()    
            
            print('Cadastro realizado com sucesso!!')
            opcao = input('Deseja sair do programa? (S/N)').upper()
            while opcao not in ['S', 'N']:
                print('Opcao invalida, tente novamente')
                opcao = input('Deseja sair do programa? (S/N)')
                
            if opcao == 'S':
                print('Programa encerrado')
                Programa.iniciar_programa(session)
            elif opcao == 'N':
                Programa.realizar_login(session)
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            print('Login Criado com sucesso!')
        finally:
            print('Funcao inserir login finalizada...')
    
    @staticmethod
    def inserir_agricultor(session):
        
        try:
            id_agricultor = Agricultores.next_id(session)
            nome_completo = input('Digite seu nome completo: ').upper()
            senha = input('Digite uma senha: ')
            confirmar_senha = input('Confirme sua senha: ')
            while senha != confirmar_senha or len(senha) > 50:
                if len(senha) > 50:
                    print('Sua senha possui mais de 50 caracteres, favor corrigir')
                else:
                    print('Suas senhas digitadas não conferem, favor corrigir')
                    
                    senha = input('Digite uma senha (maximo 50 caracteres): ')
                    confirmar_senha = input('Confirme sua senha')
            cep = input('Digite seu CEP:')
            logradouro = input('Digite seu Endereco: ').upper()
            complemento = input('Digite o Complemento: ').upper()
            localidade = input('Digite o Municipio: ').upper()
            bairro = input('Digite o Bairro: ').upper()
            uf = input('Digite a UF: ').upper()
            
            agricultor = Agricultores(id_agricultor = id_agricultor,
                            nome_completo= nome_completo,
                            senha = senha,
                            confirmar_senha = confirmar_senha,
                            cep = cep,
                            logradouro = logradouro,
                            complemento = complemento,
                            localidade = localidade,
                            bairro = bairro,
                            uf = uf,
                            email=Cadastro.email_login)
            
            session.add(agricultor)
            
            session.commit()
            
            print('Agricultor cadastrado com sucesso!!')
            
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
            return
        else:    
            return Programa.tela_inicio(session)
        finally:
            print('Finalizando funcao de inserir agricultor')
    
    @staticmethod
    def inserir_fazenda(session):
        try:
            id_fazenda = Fazenda.next_id(session)
            nome_fazenda = input('Digite o nome da Fazenda: ').upper()
            localizacao_fazenda = input('Digite a localizacao da fazenda: ').upper()
            
            id_agricultor = int(input('Digite o ID do agricultor que se refere essa fazenda: '))
            
            agricultor = session.query(Agricultores).get(id_agricultor)
            
            if agricultor is None:
                print('Codigo de agricultor invalido')
                return
            
            fazenda = Fazenda(id_fazenda = id_fazenda,
                            nome_fazenda = nome_fazenda,
                            localizacao_fazenda = localizacao_fazenda,
                            id_agricultor = id_agricultor,
                            agricultores = agricultor)
        
            session.add(fazenda)
            
            session.commit()
            
            print('Fazenda cadastrada com sucesso!!')
            
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            return Programa.tela_inicio(session)
        finally:
            print('Finalizando funcao de inserir fazenda')
        
    @staticmethod
    def inserir_vendas(session):
        
        try:
            id_venda = Vendas.next_id(session)
            id_fazenda = int(input('Digite o ID da fazenda que se refere essa venda'))
            fazenda = session.query(Fazenda).get(id_fazenda)
            
            if fazenda is None:
                print('Codigo de fazenda invalido')
                return
            
            data_venda_input = input('Insira a data da venda no formato DD/MM/AAAA: ')
            
            try:
                data_venda = datetime.strptime(data_venda_input, '%d/%m/%Y')
                data_venda_formatada = data_venda.strftime('%d/%m/%Y')
                print('Data valida', data_venda_formatada)
            except ValueError:
                print('Data invalida, tente novamente')
                return
            
            qtde_vendida = int(input('Digite a quantidade vendida: '))
            preco_venda = Decimal(input('Digite o Valor da venda: '))
            
            vendas = Vendas(id_venda = id_venda,
                            id_fazenda = id_fazenda,
                            fazenda = fazenda,
                            data_venda = data_venda_formatada,
                            qtd_vendida = qtde_vendida,
                            preco_venda = preco_venda)
            
            session.add(vendas)
            
            session.commit()
            
            print('Venda cadastrada com sucesso')
            
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            return Programa.tela_inicio(session)
        finally:
            print('Finalizando funcao de inserir vendas')
    
    @staticmethod
    def inserir_funcionarios(session):
        
        try:
            id_funcionarios = Funcionarios.next_id(session)
            nome_completo = input('Digite o nome completo do funcionario: ').upper()
            cargo = input('Digite o Cargo do funcionario: ').upper()
            salario = Decimal(input('Digite o valor do Salario: '))
            id_fazenda = int(input('Digite o ID da fazenda que se refere esse funcionario: '))
            fazenda = session.query(Fazenda).get(id_fazenda)
            
            if fazenda is None:
                print('Codigo de fazenda invalido')
                return
            
            funcionarios = Funcionarios(id_funcionario = id_funcionarios,
                                        nome_completo = nome_completo,
                                        cargo = cargo,
                                        salario = salario,
                                        id_fazenda = id_fazenda,
                                        fazenda = fazenda)
            session.add(funcionarios)
            
            session.commit()
            
            print('Funcionario cadastrado com sucesso!!')
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:    
            return Programa.tela_inicio(session)
        finally:
            print('Finalizando funcao de inserir funcionarios')
    
    @staticmethod
    def inserir_pragas(session):
        
        try:
            id_pragas = Pragas.next_id(session)
            nome_praga = input('Digite o nome da praga: ').upper()
            metodo_controle = input('Digite o metodo utilizado para erradicar: ').upper()
            id_fazenda = int(input('Digite o ID da fazenda que se refere essa praga: '))
            fazenda = session.query(Fazenda).get(id_fazenda)
            
            if fazenda is None:
                print('Codigo de fazenda invalido')
                return
            
            pragas = Pragas(id_pragas = id_pragas,
                            nome_praga = nome_praga,
                            metodo_controle_praga = metodo_controle,
                            id_fazenda = id_fazenda,
                            fazenda = fazenda)
            
            session.add(pragas)
            
            session.commit()
            
            print('Praga cadastrada com sucesso!!')
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            return Programa.tela_inicio(session)
        finally:
            print('Finalizando funcao de inserir pragas')
            
    @staticmethod
    def inserir_colheitas(session):
        
        try:
            id_colheita = Colheitas.next_id(session)
            tipo_cultura = input('Digite o nome da cultura (semente) a ser plantada: ').upper()
            
            data_plantio_input = input('Digite a data que a semente foi plantada no formato DD/MM/YYYY: ')
            try:
                data_plantio = datetime.strptime(data_plantio_input, '%d/%m/%Y')
                data_plantio_formatada = data_plantio.strftime('%d/%m/%Y')
                print('Data valida', data_plantio_formatada)
            except ValueError:
                print('Data invalida, tente novamente')
                return
            
            data_colheita_input = input('Digite a data da colheita no formato DD/MM/AAAA: ')
            try:
                data_colheita = datetime.strptime(data_colheita_input, '%d/%m/%Y')
                data_colheita_formatada = data_colheita.strftime('%d/%m/%Y')
                print('Data valida', data_colheita_formatada)
            except ValueError:
                print('Data invalida, tente novamente')
                return
            
            data_fornecida_input = input('Digite a data do fornecimento no formato DD/MM/AAAA: ')
            try:
                data_fornecida = datetime.strptime(data_fornecida_input, '%d/%m/%Y')
                data_fornecida_formatada = data_fornecida.strftime('%d/%m/%Y')
                print('Data valida', data_fornecida_formatada)
            except ValueError:
                print('Data invalida, tente novamente')
                return
            
            qtd_colhida = int(input('Digite a quantidade colhida: '))
            
            id_fazenda = int(input('Digite o ID da fazenda que se refere essa Colheita: '))
            fazenda = session.query(Fazenda).get(id_fazenda)
            
            if fazenda is None:
                print('Codigo de fazenda invalido')
                return
            
            colheitas = Colheitas(id_colheita = id_colheita,
                                tipo_cultura = tipo_cultura,
                                data_plantio = data_plantio_formatada,
                                data_colheita = data_colheita_formatada,
                                data_fornecida = data_fornecida_formatada,
                                qtd_colhida = qtd_colhida,
                                id_fazenda = id_fazenda,
                                fazenda = fazenda)
            
            session.add(colheitas)
            
            session.commit()
            
            print('Inclusao realizada com sucesso!!')
            
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            return Programa.tela_inicio(session)
        finally:
            print('Finalizando a funcao de inserir colheitas')
    
    @staticmethod
    def inserir_insumos(session):
        
        id_insumo = Insumos.next_id(session)
        nome_insumo = input('Digite o nome do insumo: ').upper()
        descricao_insumo = input('Digite uma breve descricao do insumo: ').upper()
        fornecedor_insumo = input('Digite o nome do fornecedor: ').upper()
        preco_insumo = Decimal(input('Digite o preco do insumo: '))
        
        insumos = Insumos(id_insumo = id_insumo,
                          nome_insumo = nome_insumo,
                          descricao_insumo = descricao_insumo,
                          fornecedor_insumo = fornecedor_insumo,
                          preco_insumo = preco_insumo)
        
        session.add(insumos)
        
        session.commit()
        
        print('Insumo cadastrado com sucesso!!')
        
        return Programa.tela_inicio(session)
    
    @staticmethod
    def inserir_fornecimento(session):
        
        try:
            id_fornecimento = Fornecimentos.next_id(session)
            qtd_fornecida = input('Digite a quantidade fornecida: ')
            
            data_fornecimento_input = input('Digite a data que o fornecimento chegou: ')
            try:
                data_fornecimento = datetime.strptime(data_fornecimento_input, '%d/%m/%Y')
                data_fornecimento_formatado = data_fornecimento.strftime('%d/%m/%Y')
                print('Data valida', data_fornecimento_formatado)
            except ValueError:
                print('Data invalida, tente novamente')
                return
            
            id_fazenda = int(input('Digite o ID da fazenda que se refere essa Colheita: '))
            fazenda = session.query(Fazenda).get(id_fazenda)
            
            if fazenda is None:
                print('Codigo de fazenda invalido')
                return
            
            id_insumo = int(input('Digite o ID do Insumo que se refere esse fornecimento: '))
            insumo = session.query(Insumos).get(id_insumo)
            
            if insumo is None:
                print('Codigo de insumo invalido')
                return
            
            fornecimentos = Fornecimentos(id_fornecimento = id_fornecimento,
                                        qtd_fornecida = qtd_fornecida,
                                        data_fornecimento = data_fornecimento_formatado,
                                        id_fazenda = id_fazenda,
                                        fazenda = fazenda,
                                        id_insumo = id_insumo,
                                        insumos = insumo)
            
            session.add(fornecimentos)
            
            session.commit()
            
            print('Fornecimento incluso com sucesso!!')
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            return Programa.tela_inicio(session)
        finally:
            print('Finalizando funcao de inserir fornecimento')
        
class Consultas:
    
    def escolha_consulta(session):
        opcao = int(input('Escolha uma das opcoes\n1)Consulta de Agricultores\n2)Consulta de Fazendas\n3)Voltar ao menu anterior\n'))
        
        if opcao == 1:
            Consultas.filtro_consulta_de_agricultores(session)
        elif opcao == 2:
            Consultas.consulta_por_id_fazenda(session)
        elif opcao == 3:
            Programa.tela_inicio(session)
    
    def filtro_consulta_de_agricultores(session):
        while True:
            opcao = int(input('Selecione as opções\n1) Buscar por ID\n2) Buscar pelo nome do agricultor\n3) SAIR\n'))
            if opcao == 1:
                id_agricultor = input('Digite o ID: ')
                resultado = Consultas.consulta_agricultores(session, id_agricultor = id_agricultor)
                for logradouro, localidade, bairro, uf, nome_fazenda, localizacao_fazenda in resultado:
                    print('Informações do Agricultor:')
                    print('Logradouro:', logradouro)
                    print('Localidade:', localidade)
                    print('Bairro:', bairro)
                    print('UF:', uf)
                    print('Informações da Fazenda:')
                    print('Nome da Fazenda:', nome_fazenda)
                    print('Localização da Fazenda:', localizacao_fazenda)
                    print()
            elif opcao == 2:
                nome = input('Digite o nome do Agricultor: ').upper()
                resultado = Consultas.consulta_agricultores(session, nome_completo = nome)
                for logradouro, localidade, bairro, uf, nome_fazenda, localizacao_fazenda in resultado:
                    print('Informações do Agricultor:')
                    print('Logradouro:', logradouro)
                    print('Localidade:', localidade)
                    print('Bairro:', bairro)
                    print('UF:', uf)
                    print('Informações da Fazenda:')
                    print('Nome da Fazenda:', nome_fazenda)
                    print('Localização da Fazenda:', localizacao_fazenda)
                    print()
            elif opcao == 3:
                return Consultas.escolha_consulta(session)
            else:
                print('Opção inválida. Digite 1, 2 ou 3')
    
    
    def consulta_por_id_fazenda(session):
        id_fazenda = int(input('Digite o ID da fazenda: '))

        resultado = Consultas.consulta_fazenda(session, id_fazenda = id_fazenda)
        
        for (
            nome_fazenda, qtd_colhida, data_plantio, data_colheita, data_fornecimento,
            nome_praga, metodo_controle_praga, id_funcionario, data_venda, qtd_vendida, preco_venda, _
        ) in resultado:
            print('Nome da Fazenda:', nome_fazenda)
            print('Quantidade Colhida:', qtd_colhida)
            print('Data de Plantio:', data_plantio)
            print('Data de Colheita:', data_colheita)
            print('Data de Fornecimento:', data_fornecimento)
            print('Nome da Praga:', nome_praga)
            print('Método de Controle da Praga:', metodo_controle_praga)
            print('ID do Funcionário:', id_funcionario)
            print('Data da Venda:', data_venda)
            print('Quantidade Vendida:', qtd_vendida)
            print('Preço de Venda:', preco_venda)
            print()

        return Consultas.escolha_consulta(session)
    
    @staticmethod
    def consulta_agricultores(session, id_agricultor = None, nome_completo = None):
        query = (
            session.query(
                Agricultores.logradouro,
                Agricultores.localidade,
                Agricultores.bairro,
                Agricultores.uf,
                Fazenda.nome_fazenda,
                Fazenda.localizacao_fazenda
            )
            .join(Fazenda, Agricultores.id_agricultor == Fazenda.id_agricultor)
        )
        
        if id_agricultor:
            query = query.filter(Agricultores.id_agricultor == id_agricultor)
        if nome_completo:
            query = query.filter(Agricultores.nome_completo == nome_completo)
            
        consulta = query.all()
        
        return consulta
    
    @staticmethod
    def consulta_fazenda(session, id_fazenda = None):
        query = (
            session.query(
                Fazenda.nome_fazenda,
                Colheitas.qtd_colhida,
                Colheitas.tipo_cultura,
                Colheitas.data_plantio,
                Colheitas.data_colheita,
                Fornecimentos.data_fornecimento,
                Pragas.nome_praga,
                Pragas.metodo_controle_praga,
                Funcionarios.id_funcionario,
                Vendas.data_venda,
                Vendas.qtd_vendida,
                Vendas.preco_venda
            )
            .join(Colheitas, Fazenda.id_fazenda == Colheitas.id_fazenda)
            .join(Fornecimentos, Fazenda.id_fazenda == Fornecimentos.id_fazenda)
            .join(Pragas, Fazenda.id_fazenda == Pragas.id_fazenda)
            .join(Funcionarios, Fazenda.id_fazenda == Funcionarios.id_fazenda)
            .join(Vendas, Fazenda.id_fazenda == Vendas.id_fazenda)
        )
        
        
        if id_fazenda:
            query = query.filter(Fazenda.id_fazenda == id_fazenda)
    
        consulta = query.all()
        
        return consulta
        
class Atualizar:
    
    @staticmethod
    def atualizar_senha_login(session):
        
        try:
            while True:
                email = input('Digite seu e-mail de login: ').upper()
                nova_senha = input('Digite sua nova senha: ')
                login = session.query(Login).filter(Login.email == email).first()
                
                if login:
                    login.senha = nova_senha
                    session.commit()
                    print('Senha atualizada com sucesso')
                    Atualizar.iniciar_atualizacao(session)
                    break
                else:
                    print('Usuario não encontrado')
                    opcao = int(input('Deseja tentar novamente?\n1)SIM\n2)NAO\n'))
                    if opcao != 1:
                        break
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            print('Atualizacao de senha concluida com sucesso')
        finally:
            print('Finalizando funcao atualizar login')
    
    @staticmethod
    def atualizar_agricultor(session):
        try:
            while True:
                id_agricultor = int(input('Digite o ID do agricultor: '))
                agricultor = session.query(Agricultores).filter(Agricultores.id_agricultor == id_agricultor).first()
                
                if agricultor:
                    cep = input('Digite o novo CEP: ').upper()
                    logradouro = input('Digite o novo logradouro: ').upper()
                    complemento = input('Digite o novo complemento (opcional): ').upper()
                    localidade = input('Digite a nova localidade: ').upper()
                    bairro = input('Digite o novo bairro: ').upper()
                    uf = input('Digite a nova UF: ').upper()
                    
                    agricultor.cep = cep
                    agricultor.logradouro = logradouro
                    agricultor.complemento = complemento
                    agricultor.localidade = localidade
                    agricultor.bairro = bairro
                    agricultor.uf = uf
                    
                    session.commit()
                    print('Informacoes do agricultor atualizadas com sucesso')
                    Atualizar.iniciar_atualizacao(session)
                    break
                else:
                    print('Agricultor nao encontrado')
                    opcao = int(input('Deseja tentar novamente?\n1)SIM\n2)NAO\n'))
                    if opcao != 1:
                        break
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            print('Atualizacao de Agricultor realizada')
        finally:
            print('Finalizando funcao de atualizacao de agricultor')
     
    @staticmethod
    def atualizar_fazenda(session):
        try:
            while True:
                id_fazenda = int(input('Digite o ID da fazenda: '))
                fazenda = session.query(Fazenda).filter(Fazenda.id_fazenda == id_fazenda).first()
                
                if fazenda:
                    nome_fazenda = input('Digite o novo nome da Fazenda: ').upper()
                    localiacao_fazenda = input('Digite a localizacao atualizada: ').upper()
                    
                    fazenda.nome_fazenda = nome_fazenda
                    fazenda.localizacao_fazenda = localiacao_fazenda
                    
                    session.commit()
                    print('Informacoes da Fazenda atualizadas com sucesso')
                    Atualizar.iniciar_atualizacao(session)
                    break
                else:
                    print('Fazenda nao encontrada')
                    opcao = int(input('Deseja tentar novamente?\n1)SIM\n2)NAO\n'))
                    if opcao != 1:
                        break
                    
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            print('Atualizacao de Agricultor realizada')
        finally:
            print('Finalizando funcao de atualizacao de fazenda')
                 
    @staticmethod
    def atualizar_funcionario(session):
        try:
            while True:
                id_funcionario = int(input('Digite o ID do funcionario: '))
                funcionario = session.query(Funcionarios).filter(Funcionarios.id_funcionario == id_funcionario).first()
                
                if funcionario:
                    nome_completo = input('Digite o novo nome do Funcionario: ').upper()
                    cargo = input('Digite o novo cargo: ').upper()
                    salario = Decimal(input('Digite o novo salario: '))
                    
                    funcionario.nome_completo = nome_completo
                    funcionario.cargo = cargo
                    funcionario.salario = salario
                    
                    session.commit()
                    print('Atualizacoes de Funcionario realizada!!')
                    Atualizar.iniciar_atualizacao(session)
                    break
                else:
                    print('Funcionario nao encontrado')
                    opcao = int(input('Deseja tentar novamente?\n1)SIM\n2)NAO\n'))
                    if opcao != 1:
                        break
                    
        except Exception as e:
            print('Ocorreu um erro: ', str(e))
        else:
            print('Atualizacao de Agricultor realizada')
        finally:
            print('Finalizando funcao de atualizacao de funcionario')
                    
    def iniciar_atualizacao(session):
        
        while True:        
            opcao = int(input('O que voce deseja atualizar?\n1)Senha do login\n2)Informacoes do Agricultor\n3)Informacoes da Fazenda\n4)Informacoes de Funcionario\n5)Menu anterior\n'))
            if opcao == 1:
                Atualizar.atualizar_senha_login(session)
                break
            elif opcao == 2:
                Atualizar.atualizar_agricultor(session)
                break
            elif opcao == 3:
                Atualizar.atualizar_fazenda(session)
                break
            elif opcao == 4:
                Atualizar.atualizar_funcionario(session)
                break
            elif opcao == 5:
                Programa.tela_inicio(session)
                break
            else:
                print('Opcao invalida, tente novamente')


class Deletar:
    
    @staticmethod
    def deletar_agricultor(session):
        while True:
            id_agricultor = int(input('Digite o id do agricultor a ser deletado: '))
            agricultor = session.query(Agricultores).filter(Agricultores.id_agricultor == id_agricultor).first()
            
            if agricultor:
                try:
                    session.delete(agricultor)
                    session.commit()
                    print('Agricultor deletado com sucesso')
                    Deletar.escolha_deletar(session)
                    break
                except IntegrityError as e:
                    session.rollback()
                    print('Ocorreu um erro de integridade: ', str(e))
                    return Deletar.escolha_deletar(session)
            else:
                print('Agricultor nao encontrado, tente novamente')
    
    @staticmethod
    def deletar_fazenda(session):
        while True:
            id_fazenda = int(input('Digite o id da fazenda a ser deletada: '))
            fazenda = session.query(Fazenda).filter(Fazenda.id_fazenda == id_fazenda).first()
            
            if fazenda:
                try:
                    session.delete(fazenda)
                    session.commit()
                    print('Fazenda deletada com sucesso')
                    Deletar.escolha_deletar(session)
                    break
                except IntegrityError as e:
                    session.rollback()
                    print('Ocorreu um erro de integridade: ', str(e))
                    return Deletar.escolha_deletar(session)
            else:
                print('Fazenda nao encontrada, tente novamente')
        
    @staticmethod
    def deletar_colheita(session):
        while True:
            id_colheita = int(input('Digite o id da colheita a ser deletado: '))
            colheita = session.query(Colheitas).filter(Colheitas.id_colheita == id_colheita).first()
            
            if colheita:
                session.delete(colheita)
                session.commit()
                print('Colheita deletada com sucesso')
                Deletar.escolha_deletar(session)
                break
            else:
                print('Colheita nao encontrada, tente novamente')
                
    @staticmethod
    def deletar_insumos(session):
        while True:
            id_insumos = int(input('Digite o ID do Insumo a ser deletado: '))
            insumos = session.query(Insumos).filter(Insumos.id_insumo == id_insumos).first()
            
            if insumos:
                session.delete(insumos)
                session.commit()
                print('Insumo deletado com sucesso')
                Deletar.escolha_deletar(session)
                break
            else:
                print('Insumo nao encontrado, tente novamente')
                
    @staticmethod
    def deletar_fornecimentos(session):
        while True:
            id_fornecimentos = int(input('Digite o ID do Fornecimento a ser deletado: '))
            fornecimentos = session.query(Fornecimentos).filter(Fornecimentos.id_fornecimento == id_fornecimentos).first()
            
            if fornecimentos:
                session.delete(fornecimentos)
                session.commit()
                print('Fornecimento deletado com sucesso')
                Deletar.escolha_deletar(session)
                break
            else:
                print('Fornecimento nao encontrado')
    
    @staticmethod
    def deletar_pragas(session):
        while True:
            id_praga = int(input('Digite o id da praga a ser deletada: '))
            pragas = session.query(Pragas).filter(Pragas.id_pragas == id_praga).first()
            
            if pragas:
                session.delete(pragas)
                session.commit()
                print('Praga deletada com sucesso')
                Deletar.escolha_deletar(session)
                break
            else:
                print('Praga nao encontrada')
                
    @staticmethod
    def deletar_funcionarios(session):
        while True:
            id_funcionario = int(input('Digite o ID do funcionario a ser deletado: '))
            funcionario = session.query(Funcionarios).filter(Funcionarios.id_funcionario == id_funcionario).first()
            
            if funcionario:
                session.delete(funcionario)
                session.commit()
                print('Funcionario deletado com sucesso')
                Deletar.escolha_deletar(session)
                break
            else:
                print('Funcionario nao encontrado, tente novamente')
    
    @staticmethod
    def deletar_vendas(session):
        while True:
            id_vendas = int(input('Digite o ID da venda a ser deletada: '))
            vendas = session.query(Vendas).filter(Vendas.id_venda == id_vendas).first()
            
            if vendas:
                session.delete(vendas)
                session.commit()
                print('Venda deletada com sucesso')
                Deletar.escolha_deletar(session)
                break
            else:
                print('Venda nao encontrada')
    
    @staticmethod
    def escolha_deletar(session):
        while True:
            opcao = int(input('O que voce quer deletar?\n1)Deletar Agricultor\n2)Deletar Fazenda\n3)Deletar Colheita\
                \n4)Deletar Insumos\n5)Deletar Fornecimentos\n6)Deletar Pragas\n7)Deletar Funcionarios\n8)Deletar Vendas\n9)Menu Anterior\n'))
            
            if opcao == 1:
                Deletar.deletar_agricultor(session)
                break
            elif opcao == 2:
                Deletar.deletar_fazenda(session)
                break
            elif opcao == 3:
                Deletar.deletar_colheita(session)
                break
            elif opcao == 4:
                Deletar.deletar_insumos(session)
                break
            elif opcao == 5:
                Deletar.deletar_fornecimentos(session)
                break
            elif opcao == 6:
                Deletar.deletar_pragas(session)
                break
            elif opcao == 7:
                Deletar.deletar_funcionarios(session)
                break
            elif opcao == 8:
                Deletar.deletar_vendas(session)
                break
            elif opcao == 9:
                Programa.tela_inicio(session)
                break
            else:
                print('Opcao invalida, tente novamente')
        
class Programa():
    
    @classmethod
    def tela_inicio(self, session):
        while True:
            escolha = int(input('O que voce deseja fazer?\n1)Cadastros\n2)Consultas\n3)Atualizacao de Cadastro\n4)Excluir Cadastros\n5)Sair\n'))
            if escolha == 1:
                while True:
                    opcao_cadastro = int(input('O que voce deseja fazer?\n1)Cadastro de Agricultor\n2)Cadastro de Fazenda\n3)Cadastrar uma venda\
                    \n4)Cadastrar um funcionario\n5)Cadastrar uma praga\n6)Cadastrar uma colheita\n7)Cadastrar um insumo\n8)Cadastrar um fornecimento\n9)Menu anterior'))
                    if opcao_cadastro == 1:
                        Cadastro.inserir_agricultor(session)
                        break
                    elif opcao_cadastro == 2:
                        Cadastro.inserir_fazenda(session)
                        break
                    elif opcao_cadastro == 3:
                        Cadastro.inserir_vendas(session)
                        break
                    elif opcao_cadastro == 4:
                        Cadastro.inserir_funcionarios(session)
                        break
                    elif opcao_cadastro == 5:
                        Cadastro.inserir_pragas(session)
                        break
                    elif opcao_cadastro == 6:
                        Cadastro.inserir_colheitas(session)
                        break
                    elif opcao_cadastro == 7:
                        Cadastro.inserir_insumos(session)
                        break
                    elif opcao_cadastro == 8:
                        Cadastro.inserir_fornecimento(session)
                        break
                    elif opcao_cadastro == 9:
                        Programa.tela_inicio(session)
                        break
                    else:
                        print('Opcao invalida, tente novamente')
            elif escolha == 2:
                Consultas.escolha_consulta(session)
                break
            elif escolha == 3:
                Atualizar.iniciar_atualizacao(session)
                break
            elif escolha == 4:
                Deletar.escolha_deletar(session)
                break
            else:
                print('Opcao invalida, tente novamente')


                    
    def iniciar_programa(session):
        while True:
            opcao = int(input('Bem vindo ao MyFarm!! Escolha entre as opcoes abaixo\n1)Fazer Login\n2)Criar um novo Cadastro\n'))
            
            if opcao == 1:
                Programa.realizar_login(session)
                break
            elif opcao == 2:
                Cadastro.inserir_login(session)
                break
            else:
                print('Opcao invalida, tente novamente')

    def realizar_login(session):
        email = input('Digite seu email: ').upper()
        Cadastro.email_login = email
        senha = input('Digite sua senha: ')
            
        login = session.query(Login).filter_by(email=email, senha=senha).first()
        
        if login is not None:
            print('Login realizado com sucesso!!')
            Programa.tela_inicio(session)
        else:
            print('Email ou senha incorretos, deseja realizar o cadastro?')
            cadastrar = input('Deseja se cadastrar? (S/N): ').upper()
            if cadastrar == 'S':
                Cadastro.inserir_login(session)
            else:
                print('Obrigado! Até a proxima')

        
Programa.iniciar_programa(session)