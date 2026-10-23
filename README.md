# CollageReport144 — versão atualizada

Aplicativo desktop para Windows. Processamento local, sem API, sem envio de arquivos e sem banco de dados.

## Recursos
- Importar múltiplas imagens ou colar imagem com Ctrl+V.
- Reordenar/remover imagens.
- Tema claro/escuro.
- Alinhamento individual aplicado a cada imagem: horizontal esquerda/centro/direita e vertical acima/centro/abaixo.
- Duas formas de ajuste: **Conter sem cortar** (preserva a imagem inteira) e **Preencher cortando** (preenche a célula recortando o excedente de acordo com o alinhamento).
- Proporções comuns de célula: Original, 1:1, 4:3, 3:2, 16:9 e 9:16. Todas as células de uma prancha usam a mesma proporção.
- Exportar PNG/JPEG, criar documento Word e gerar entre 3 e 10 variações PNG em lote.
- As variações mudam o número de colunas e a ordem das imagens.

## Instalação e uso
1. Extraia o ZIP.
2. Instale Python 3.10+ se necessário.
3. Execute `instalar_dependencias.bat` (precisa de internet somente para instalar bibliotecas).
4. Execute `executar_CollageReport144.bat`.

## Criar o executável
1. Execute `gerar_executavel.bat`.
2. O arquivo será criado em `dist\CollageReport144.exe`.
3. Após a compilação, o executável pode ser usado offline.

## Nota sobre o alinhamento
O alinhamento é aplicado a cada imagem dentro da sua célula, individualmente. Em modo “Conter sem cortar”, a imagem mantém a proporção original e o espaço restante fica com a cor de fundo. Em “Preencher cortando”, a célula é preenchida e o excedente é recortado, com a posição do corte controlada pelo alinhamento.
