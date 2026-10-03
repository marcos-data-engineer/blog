# Revisão final da apresentação

A apresentação em português é gerada pelo script `_scripts/gerar_slides_completos.py` e salva como `apresentacao_final.pptx` nesta pasta. Este guia substitui as instruções antigas que se referiam à versão em espanhol.

## Conferências antes de gravar

- **Slides 1 e 2:** confira o título e substitua o espaço reservado por uma captura atual do site.
- **Slide 5:** a hospedagem sem custo refere-se ao GitHub Pages; não prometa domínio próprio gratuito.
- **Slide 7:** mantenha a promessa alinhada ao conteúdo real do curso e aos requisitos de instalação.
- **Slide 8:** apresente a comparação entre Jekyll e WordPress de forma equilibrada; custos e desempenho variam conforme a configuração.
- **Slide 9:** insira uma captura real do site e remova qualquer espaço reservado antes de exportar.
- **Slide 10:** confirme se os requisitos continuam corretos para o público do curso.
- **Slide 12:** confira os dados de contato e a URL exibida.

## Regenerar o arquivo

Na raiz do repositório, instale as dependências descritas em `requirements.txt` e execute:

```bash
python _course_production/_scripts/gerar_slides_completos.py
```

O script atualiza `apresentacao_final.pptx` nesta pasta. Depois de regenerar, abra o arquivo no Google Slides ou no PowerPoint e revise o ajuste do texto, as capturas de tela e os dados de contato.
