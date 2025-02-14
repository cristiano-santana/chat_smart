from flask import Blueprint, render_template, request, jsonify
from .services.openai_service import traduzir_para_query
from .services.db_service import executar_query
from .utils import dados_para_tabela_html 

bp = Blueprint('main', __name__)

# Definição do schema do banco de dados
SCHEMA = """
"os": {
    "descricao": "Tabela de 'os' (ordens de serviço).",
    "colunas": ("id","os_concessionaria","tipo_atendimento","retencao_iss","paga","data_pagamento","fechada","data_fechamento","finalizada","data_finalizacao","cancelada","data_cancelamento","solicitado_cancelamento","os_retorno","cortesia_migrada","nivel_indicador1","nivel_indicador2","indicador1_id","indicador2_id","departamento_id","vendedor_id","concessionaria_id","cliente_carro_id","cliente_id","os_tipo_id","proposta_id","os_retorno_id","os_migracao_cortesia_id","ativo","created_at","deleted_at","id_antigo"),
    "relacionamentos": {
        "cliente_carros": "cliente_carros.id = os.cliente_carro_id",
        "clientes": "clientes.id = os.cliente_id",
        "concessionarias": "concessionarias.id = os.concessionaria_id",
        "departamentos": "departamentos.id = os.departamento_id",
        "funcionarios": "funcionarios.id = os.vendedor_id",
        "indicadores": "indicadores.id = os.indicador2_id",
        "os": "os.id = os.os_retorno_id",
        "os_tipos": "os_tipos.id = os.os_tipo_id",
        "pre_propostas": "pre_propostas.id = os.pre_proposta_id",
        "propostas": "propostas.id = os.proposta_id"
    }
},
"os_servicos": {
    "descricao": "Tabela de os_servicos (serviços de ordens de serviço). tabela pivot entre 'os' e 'servicos'.",
    "colunas": ("id","codigo","valor_venda","valor_original","desconto_supervisao","desconto_migracao_cortesia","desconto_avista","valor_venda_real","os_tipo_id","desconto_bonus","fechado","codigo_fechamento","data_fechamento","fechado_sem_codigo","justificativa_sem_codigo","cancelado","data_cancelamento","solicitado_cancelamento","os_id","servico_id","tonalidade_id","combo_id","produtivo_id","concessionaria_execucao_id","ativo","created_at","deleted_at","plotter_corte_id"),
    "relacionamentos": {
        "combos": "combos.id = os_servicos.combo_id",
        "os": "os.id = os_servicos.os_id",
        "os_tipos": "os_tipos.id = os_servicos.os_tipo_id",
        "plotter_cortes": "plotter_cortes.id = os_servicos.plotter_corte_id",
        "funcionarios": "funcionarios.id = os_servicos.produtivo_id",
        "servicos": "servicos.id = os_servicos.servico_id",
        "tonalidades": "tonalidades.id = os_servicos.tonalidade_id",
        "concessionarias": "concessionarias.id = os_servicos.concessionaria_execucao_id"
    }
},
 "servicos": {
    "descricao": "Tabela de servicos (serviços).",
    "colunas": ("id","nome","custo_fixo","codigo_nf","fecha_kit","fecha_peca_avulsa","fecha_peca","fecha_produto","fecha_produtivo","diferencia_departamento_preco","diferencia_porte","diferencia_departamento","diferencia_porte_comissao","diferencia_tempo_departamento","diferencia_tempo_cor","credito_necessario","valor_desconto_cortesia","aceita_desconto_cortesia","segunda_aplicacao","grupo_servico_id","subgrupo_servico_id","servico_categoria_id","tags","ativo","created_at","deleted_at"),
    "relacionamentos": {
        "grupos_servicos": "grupos_servicos.id = servicos.grupo_servico_id",
        "servico_categorias": "servico_categorias.id = servicos.servico_categoria_id",
        "subgrupos_servicos": "subgrupos_servicos.id = servicos.subgrupo_servico_id"
    }
},
"caixa_status": {
    "descricao": "Tabela de caixa status",
    "colunas": ("id","nome","ativo"),
    "relacionamentos": {}
},
"caixa_tipos": {
    "descricao": "Tabela de caixa tipos",
    "colunas": ("id","nome","ativo"),
    "relacionamentos": {}
},
"caixas": {
    "descricao": "Tabela de caixas (movimentações financeiras, se tiver um ou mais registros na tabela caixas a 'os' referente a este caixa foi paga!).",
    "colunas": ("id","valor","data_vencimento","data_pagamento","cancelado","data_cancelamento","fechado","data_fechamento","classificado","data_classificacao","finalizado","verificado","data_verificacao","data_finalizacao","parcela","quant_parcelas","nome_depositante","codigo_transacao","nome_titular","doc_titular","telefone_titular","tid_cielo","bandeira_cartao","codigo_autorizacao","numero_autorizacao","nome_cartao","cc_conciliado","pix_payload","pix_info_pagador","pix_e2ed_id","pix_rtr_id","observacao_financeiro","caixa_preto","usuario_pagamento_id","usuario_verificacao_id","caixa_conta_id","caixa_tipo_id","caixa_pendente_id","caixa_status_id","caixa_fechamento_id","caixa_original_id","empresa_faturamento_id","financeiro_malote_classificacao_id","financeiro_caixa_destino_id","os_id","ativo","created_at","deleted_at"),
    "relacionamentos": {
        "caixa_contas": "caixa_contas.id = caixas.caixa_conta_id",
        "caixa_fechamentos": "caixa_fechamentos.id = caixas.caixa_fechamento_id",
        "caixas": "caixas.id = caixas.caixa_original_id",
        "caixas_pendentes": "caixas_pendentes.id = caixas.caixa_pendente_id",
        "caixa_status": "caixa_status.id = caixas.caixa_status_id",
        "caixa_tipos": "caixa_tipos.id = caixas.caixa_tipo_id",
        "empresas": "empresas.id = caixas.empresa_faturamento_id",
        "financeiro_caixas_destino": "financeiro_caixas_destino.id = caixas.financeiro_caixa_destino_id",
        "financeiro_malotes_classificacao": "financeiro_malotes_classificacao.id = caixas.financeiro_malote_classificacao_id",
        "os": "os.id = caixas.os_id",
        "usuarios": "usuarios.id = caixas.usuario_verificacao_id"
    }
},
"caixas_pendentes": {
    "descricao": "Tabela de caixas pendentes (movimentações financeiras pendentes, se tiver registro existe uma promessa de pagamento).",
    "colunas": ("id","valor","codigo_transacao","expiracao","pix_tx_id","pix_payload","pix_tentativas","pix_br_code","pix_info_pagador","pix_e2ed_id","pix_rtr_id","data_criacao_cobranca","data_expiracao_cobranca","fechado","data_fechamento","finalizado","data_finalizacao","cancelado","data_cancelamento","caixa_tipo_id","caixa_status_id","caixa_fechamento_id","os_id","empresa_id","remessa_os_id","tipo_remessa_id","usuario_pagamento_id","created_at","deleted_at"),
    "relacionamentos": {
        "caixa_fechamentos": "caixa_fechamentos.id = caixas_pendentes.caixa_fechamento_id",
        "caixa_status": "caixa_status.id = caixas_pendentes.caixa_status_id",
        "caixa_tipos": "caixa_tipos.id = caixas_pendentes.caixa_tipo_id",
        "empresas": "empresas.id = caixas_pendentes.empresa_id",
        "os": "os.id = caixas_pendentes.os_id",
        "remessa_os": "remessa_os.id = caixas_pendentes.remessa_os_id",
        "usuarios": "usuarios.id = caixas_pendentes.usuario_pagamento_id",
        "tipo_remessas": "tipo_remessas.id = caixas_pendentes.tipo_remessa_id"
    }
},
"concessionarias": {
    "descricao": "Tabela de concessionarias (concessionárias de veículos, onde nós vendemos serviços como terceiro!).",
    "colunas": ("id","nome","aceita_indicador1","aceita_indicador2","produtivo_base_id","concessionaria_execucao_id","cluster_id","business_unit_id","empresa_faturamento_id","ativo","created_at","deleted_at"),
    "relacionamentos": {
        "business_units": "business_units.id = concessionarias.business_unit_id",
        "concessionarias": "concessionarias.id = concessionarias.concessionaria_execucao_id",
        "clusters": "clusters.id = concessionarias.cluster_id",
        "carro_marcas": "carro_marcas.id = concessionarias.carro_marca_id",
        "comissao_periodos": "comissao_periodos.id = concessionarias.comissao_periodo_id",
        "empresas": "empresas.id = concessionarias.empresa_faturamento_id",
        "nota_tipos": "nota_tipos.id = concessionarias.nota_tipo_id",
        "produtivo_bases": "produtivo_bases.id = concessionarias.produtivo_base_id",
        "funcionarios": "funcionarios.id = concessionarias.supervisor_vendas_id"
    }
},
"departamentos": {
    "descricao": "Tabela de departamentos (departamentos de vendas).",
    "colunas": ("id","nome","sigla","sigla_carbel","ativo","created_at","deleted_at"),
    "relacionamentos": {}
},
"nf_devolucao_itens": {
    "descricao": "Tabela de nota fiscal de devolucao de itens, itens devolvidos de uma nota fiscal.",
    "colunas": ("id","motivo_devolucao","codigo","descricao","quantidade","medida","valor_unitario","ncm","cfop","cst","valor_ipi","aliquota_ipi","valor_icms","aliquota_icms","base_calculo_icms","valor_icms_st","valor_total","valor_frete","valor_seguro","porcentagem_devolucao","origem","nota_fiscal_id","created_at","updated_at","deleted_at","nf_devolucao_itens_nota_fiscal_id_foreign"),
    "relacionamentos": {
        "notas_fiscais": "notas_fiscais.id = nf_devolucao_itens.nota_fiscal_id"
    }
},
"nota_fiscal_statuses": {
    "descricao": "Tabela de nota fiscal status",
    "colunas": ("id","nome","created_at","updated_at","deleted_at"),
    "relacionamentos": {}
},
"nota_tipos": {
    "descricao": "Tabela de nota fiscal tipos",
    "colunas": ("id","nome","ativo","created_at","updated_at","deleted_at"),
    "relacionamentos": {}
},
"notas_fiscais": {
    "descricao": "Tabela de notas fiscais",
    "colunas": ("id","valor_bruto","valor_liquido","retencao_iss","data_emissao","tipo_nota","serie","bancotoyota","numero_nota","chave_nota","numero_registro","status_nota","danfe_emitida","email_enviado","url_danfe","resposta_erro","cancelada","data_cancelamento","solicitado_cancelamento","motivo_cancelamento","devolvida","data_devolucao","solicitado_devolucao","cancelamento_extemporaneo","data_cancelamento_extemporaneo","solicitado_cancelamento_extemporaneo","observacao_devolucao","devolucao_pelo_cliente","chave_nfe_referencia","chave_cte_referencia","observacao","info_adicional","natureza_operacao","boleto_emitido","url_boleto","data_emissao_boleto","data_vencimento_boleto","boleto_registrado","data_registro_boleto","lancado_moneycare","data_lancamento_moneycare","os_id","cortesia_id","fornecedor_id","parent_id","boleto_remessa_id","empresa_id","ativo","created_at","updated_at","deleted_at"),
    "relacionamentos": {
        "boleto_remessas": "boleto_remessas.id = notas_fiscais.boleto_remessa_id",
        "cortesias": "cortesias.id = notas_fiscais.cortesia_id",
        "empresas": "empresas.id = notas_fiscais.empresa_id",
        "fornecedores": "fornecedores.id = notas_fiscais.fornecedor_id",
        "os": "os.id = notas_fiscais.os_id",
        "notas_fiscais": "notas_fiscais.id = notas_fiscais.parent_id",
        "nota_fiscal_statuses": "nota_fiscal_statuses.id = notas_fiscais.status_nota"
    }
},
"estornos": {
    "descricao": "Tabela de estornos (estornos de movimentações financeiras se uma 'os' tem um ou mais registros aqui, o caixa dessa 'os' foi estornado!).",
    "colunas": ("id","tipo","valor","motivo","status","pix_rtr_id","justificativa","solicitado_por","atendido_por","os_id","caixa_id","created_at","updated_at","deleted_at","estornos_solicitado_por_foreign","estornos_atendido_por_foreign","estornos_os_id_foreign","estornos_caixa_id_foreign"),
    "relacionamentos": {
        "funcionarios": "funcionarios.id = estornos.solicitado_por",
        "caixas": "caixas.id = estornos.caixa_id",
        "os": "os.id = estornos.os_id"
    }
},
"estoque_saida_produtos": {
    "descricao": "Tabela de estoque saida produtos (produtos que saíram do estoque).",
    "colunas": ("id,"cancelado,"data_cancelamento,"motivo_cancelamento,"entregue,"data_entrega,"os_servico_entrega_id,"funcionario_entrega_id,"recebido,"data_recebimento,"funcionario_recebimento_id,"devolvido,"data_devolucao,"produto_id,"estoque_saida_id,"estoque_entrada_produto_id,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "estoque_entrada_produtos": "estoque_entrada_produtos.id = estoque_saida_produtos.estoque_entrada_produto_id",
        "estoque_saidas": "estoque_saidas.id = estoque_saida_produtos.estoque_saida_id",
        "produtos": "produtos.id = estoque_saida_produtos.produto_id",
        "funcionarios": "funcionarios.id = estoque_saida_produtos.funcionario_recebimento_id",
        "os_servicos": "os_servicos.id = estoque_saida_produtos.os_servico_entrega_id"
    }
},
"estoque_saida_status": {
    "descricao": "Tabela de estoque saida status (status de saída de estoque).",
    "colunas": ("id","nome","created_at","updated_at","deleted_at"),
    "relacionamentos": {}
},
"estoque_saida_tipos": {
    "descricao": "Tabela de estoque saida tipos (tipos de saída de estoque).",
    "colunas": ("id,"nome,"exibir,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {}
},
"estoque_saidas": {
    "descricao": "Tabela de estoque saidas (saídas de estoque).",
    "colunas": ("id,"observacao,"solicitado_cancelamento,"motivo_cancelamento,"cancelada,"data_cancelamento,"funcionario_registro_id,"estoque_saida_tipo_id,"estoque_saida_status_id,"concessionaria_id,"concessionaria_execucao_id,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "concessionarias": "concessionarias.id = estoque_saidas.concessionaria_id",
        "estoque_saida_status": "estoque_saida_status.id = estoque_saidas.estoque_saida_status_id",
        "estoque_saida_tipos": "estoque_saida_tipos.id = estoque_saidas.estoque_saida_tipo_id",
        "funcionarios": "funcionarios.id = estoque_saidas.funcionario_registro_id"
    }
},
"estoque_entrada_produtos": {
    "descricao": "Tabela de estoque entrada produtos (produtos que entraram no estoque). Aqui ficam os produtos que compõem as notas fiscais de entrada.",
    "colunas": ("id,"valor_unitario,"valor_sugerido,"valor_unitario_real,"valor_icms,"valor_icms_subst,"base_icms,"valor_ipi,"aliquota_ipi,"codigo,"codigo_antigo,"individual,"quantidade_usos,"tamanho,"estoque_minimo,"finalizado,"data_finalizacao,"transferido,"data_transferencia,"impresso,"data_impressao,"observacao,"usuario_transferencia_id,"estoque_entrada_id,"estoque_id,"estoque_original_id,"produto_id,"tonalidade_id,"carro_modelo_id,"os_servico_id,"ativo,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "carro_modelos": "carro_modelos.id = estoque_entrada_produtos.carro_modelo_id",
        "estoque_entradas": "estoque_entradas.id = estoque_entrada_produtos.estoque_entrada_id",
        "estoque_fracionamentos": "estoque_fracionamentos.id = estoque_entrada_produtos.estoque_fracionamento_id",
        "estoques": "estoques.id = estoque_entrada_produtos.estoque_original_id",
        "os_servicos": "os_servicos.id = estoque_entrada_produtos.os_servico_id",
        "produtos": "produtos.id = estoque_entrada_produtos.produto_id",
        "tonalidades": "tonalidades.id = estoque_entrada_produtos.tonalidade_id",
        "usuarios": "usuarios.id = estoque_entrada_produtos.usuario_transferencia_id"
    }
},
"estoque_entradas": {
    "descricao": "Tabela de estoque entradas (entradas de estoque). Aqui ficam as notas fiscais de entrada de produtos no estoque.",
    "colunas": ("id,"nota,"recuperacao,"data_emissao,"total_ipi,"total_icms_st,"total_produtos,"total_tributos,"total_nota,"possui_frete,"frete,"data_vencimento,"seguro,"desconto,"despesa_acessoria,"cancelada,"data_cancelamento,"solicitado_cancelamento,"estoque_id,"fornecedor_id,"transportadora_id,"ordem_compra_id,"ativo,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "estoques": "estoques.id = estoque_entradas.estoque_id",
        "fornecedores": "fornecedores.id = estoque_entradas.fornecedor_id",
        "ordens_compras": "ordens_compras.id = estoque_entradas.ordem_compra_id",
        "transportadoras": "transportadoras.id = estoque_entradas.transportadora_id"
    }
},
"fornecedor_produtos": {
    "descricao": "Tabela produtos de um fornecedor",
    "colunas": ("id,"valor_unitario,"valor_icms,"aliquota_ipi,"fornecedor_id,"produto_id,"ativo,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "fornecedores": "fornecedores.id = fornecedor_produtos.fornecedor_id",
        "produtos": "produtos.id = fornecedor_produtos.produto_id"
    }
},
"fornecedores": {
    "descricao": "Tabela de fornecedores",
    "colunas": ("id,"nome,"razao_social,"cnpj,"ie,"im,"cep,"logradouro,"bairro,"localidade,"uf,"numero,"complemento,"contato,"telefone1,"telefone2,"email,"ativo,"estoque_id,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "estoques": "estoques.id = fornecedores.estoque_id"
    }
},
"grupos_produtos": {
    "descricao": "Tabela de grupos produtos",
    "colunas": ("id","nome","ativo","created_at","updated_at","deleted_at"),
    "relacionamentos": {}
},
"grupos_servicos": {
    "descricao": "Tabela de grupos servicos",
    "colunas": ("id","nome","ativo","created_at","updated_at","deleted_at"),
    "relacionamentos": {}
},
"ordens_compras": {
    "descricao": "Tabela de ordens compras",
    "colunas": ("id,"proposta_compra_id,"estoque_id,"fornecedor_id,"ordem_compra_status_id,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "estoques": "estoques.id = ordens_compras.estoque_id",
        "fornecedores": "fornecedores.id = ordens_compras.fornecedor_id",
        "ordem_compra_status": "ordem_compra_status.id = ordens_compras.ordem_compra_status_id"
    }
},
"ordem_compra_produtos": {
    "descricao": "Tabela produtos de uma ordem compra",
    "colunas": ("id,"quantidade,"quantidade_antecipacao,"quantidade_antecipada,"quantidade_pendente,"valor_unitario,"editado_entrega,"produto_id,"produto_tamanho_id,"tonalidade_id,"carro_modelo_id,"ordem_compra_id,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "ordens_compras": "ordens_compras.id = ordem_compra_produtos.ordem_compra_id",
        "produtos": "produtos.id = ordem_compra_produtos.produto_id",
        "produto_tamanhos": "produto_tamanhos.id = ordem_compra_produtos.produto_tamanho_id",
        "carro_modelos": "carro_modelos.id = ordem_compra_produtos.carro_modelo_id",
        "tonalidades": "tonalidades.id = ordem_compra_produtos.tonalidade_id"
    }
},
"ordem_compra_status": {
    "descricao": "Tabela status de uma ordem compra",
    "colunas": ("id","nome","created_at","updated_at","deleted_at"),
    "relacionamentos": {}
},
"os_retorno_servicos": {
    "descricao": "Tabela servicos refeito de 'os' de retorno",
    "colunas": ("id","os_retorno_id","os_servico_id","servico_id","ativo","created_at","updated_at","deleted_at"),
    "relacionamentos": {
        "os_retornos": "os_retornos.id = os_retorno_servicos.os_retorno_id",
        "os_servicos": "os_servicos.id = os_retorno_servicos.os_servico_id",
        "servicos": "servicos.id = os_retorno_servicos.servico_id"
    }
},
"os_retornos": {
    "descricao": "Tabela de 'os' que o cliente voltou reclamando da qualidade do servico",
    "colunas": ("id","descricao","data_solicitacao","data_aprovacao","data_recusa","os_origem_id","os_destino_id","retorno_motivo_id","retorno_classificacao_id","usuario_solicitacao_id","usuario_aprovacao_id","usuario_recusa_id","aprovado","recusado","ativo","created_at","updated_at","deleted_at"),
    "relacionamentos": {
        "os": "os.id = os_retornos.os_origem_id",
        "retorno_motivos": "retorno_motivos.id = os_retornos.retorno_motivo_id",
        "funcionarios": "funcionarios.id = os_retornos.usuario_solicitacao_id",
        "retorno_classificacoes": "retorno_classificacoes.id = os_retornos.retorno_classificacao_id"
    }
},
"produto_tonalidades": {
    "descricao": "Tabela de produto_tonalidades (tonalidades de produtos). tabela pivot entre 'produtos' e 'tonalidades'.",
    "colunas": ("id","produto_id","tonalidade_id","created_at","updated_at","deleted_at"),
    "relacionamentos": {
        "produtos": "produtos.id = produto_tonalidades.produto_id",
        "tonalidades": "tonalidades.id = produto_tonalidades.tonalidade_id"
    }
},
"produtos": {
    "descricao": "Tabela de produtos usados em serviços",
    "colunas": ("id","nome","codigo","envio_maximo","fracionavel","fracao_rastreavel","rastreavel","fecha_servico","diferencia_tonalidade","diferencia_modelo","diferencia_tamanho","medida_id","grupo_produto_id","subgrupo_produto_id","ativo","created_at","updated_at","deleted_at"),
    "relacionamentos": {
        "grupos_produtos": "grupos_produtos.id = produtos.grupo_produto_id",
        "medidas": "medidas.id = produtos.medida_id",
        "subgrupos_produtos": "subgrupos_produtos.id = produtos.subgrupo_produto_id"
    }
},
"servico_categorias": {
    "descricao": "Tabela de categorias de servicos",
    "colunas": ("id","nome","ativo","created_at","updated_at","deleted_at"),
    "relacionamentos": {}
},
"servico_departamentos": {
    "descricao": "Tabela de servicos que podem ser vendidos nos departamentos da concessionaria",
    "colunas": ("id","servico_id","servico_acessorio_id","departamento_id","ativo","created_at","updated_at","deleted_at"),
    "relacionamentos": {
        "departamentos": "departamentos.id = servico_departamentos.departamento_id",
        "servicos": "servicos.id = servico_departamentos.servico_id"
    }
},
"servico_produto_departamentos": {
    "descricao": "Tabela de servico produto departamentos (departamentos de servicos e produtos). tabela pivot entre 'servico_produtos' e 'departamentos'.",
    "colunas": ("id,"servico_produto_id,"departamento_id,"ativo,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "departamentos": "departamentos.id = servico_produto_departamentos.departamento_id",
        "servico_produtos": "servico_produtos.id = servico_produto_departamentos.servico_produto_id"
    }
},
"servico_produto_portes": {
    "descricao": "Tabela de servico produto portes (portes de servicos e produtos). tabela pivot entre 'servico_produtos' e 'carro_portes'.",
    "colunas": ("id,"servico_produto_id,"carro_porte_id,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "carro_portes": "carro_portes.id = servico_produto_portes.carro_porte_id",
        "servico_produtos": "servico_produtos.id = servico_produto_portes.servico_produto_id"
    }
},
"servico_produtos": {
    "descricao": "Tabela de servico produtos (produtos de serviços). tabela pivot entre 'servicos' e 'produtos'.",
    "colunas": ("id,"alternavel,"filtro_cor,"filtro_departamento,"servico_id,"produto_id,"ativo,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "produtos": "produtos.id = servico_produtos.produto_id",
        "servicos": "servicos.id = servico_produtos.servico_id"
    }
},
"servicos": {
    "descricao": "Tabela de servicos",
    "colunas": ("id,"nome,"custo_fixo,"codigo_nf,"fecha_kit,"fecha_peca_avulsa,"fecha_peca,"fecha_produto,"fecha_produtivo,"diferencia_departamento_preco,"diferencia_porte,"diferencia_departamento,"diferencia_porte_comissao,"diferencia_tempo_departamento,"diferencia_tempo_cor,"credito_necessario,"valor_desconto_cortesia,"aceita_desconto_cortesia,"segunda_aplicacao,"grupo_servico_id,"subgrupo_servico_id,"servico_categoria_id,"tags,"ativo,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "grupos_servicos": "grupos_servicos.id = servicos.grupo_servico_id",
        "servico_categorias": "servico_categorias.id = servicos.servico_categoria_id",
        "subgrupos_servicos": "subgrupos_servicos.id = servicos.subgrupo_servico_id"
    }
},
"subgrupos_produtos": {
    "descricao": "Tabela de subgrupos produtos.",
    "colunas": ("id,"nome,"grupo_produto_id,"ativo,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "grupos_produtos": "grupos_produtos.id = subgrupos_produtos.grupo_produto_id"
    }
},
"subgrupos_servicos": {
    "descricao": "Tabela de subgrupos servicos",
    "colunas": ("id,"nome,"sigla,"grupo_servico_id,"ativo,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {
        "grupos_servicos": "grupos_servicos.id = subgrupos_servicos.grupo_servico_id"
    }
},
"tonalidades": {
    "descricao": "Tabela de tonalidades",
    "colunas": ("id,"nome,"ativo,"created_at,"updated_at,"deleted_at),
    "relacionamentos": {}
},
"""

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/pergunta', methods=['POST'])
def pergunta():
    data = request.get_json()
    pergunta = data.get('pergunta')
    
    if not pergunta:
        return jsonify({"erro": "Pergunta não fornecida."}), 400

    # Traduzir pergunta para query SQL
    query_sql = traduzir_para_query(SCHEMA, pergunta)
    
    # Executar a query no banco de dados
    resultados = executar_query(query_sql)
    
    # Converter os resultados para uma tabela HTML
    tabela_html = dados_para_tabela_html(resultados) if isinstance(resultados, list) else resultados
    
    return jsonify({
        "query": query_sql,
        "tabela_html": tabela_html
    })