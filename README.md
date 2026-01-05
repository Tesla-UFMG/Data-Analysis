# Data-Analysis
Fórmula Tesla UFMG's data analysis software and repository


## 🏗️ Estrutura do Repositório

```
📂 Data-Analysis/
├── 📂 2020_data_analysis/         # Software em JS feito pela equipe em 2020 para análise de dados. Não usado.
├── 📂 data/                       # Arquivos CSV com os dados coletados
│   ├── 📂 dados_telemetria/       # CSVs coletados de testes de rua do carro
├── 📂 misc/                       # Arquivos python e Jupyter gerais
├── 📂 notebooks/                  # Notebooks Jupyer para analise dos dados da telemtria (testes de rua do carro)
└── 📂 relatorios/                 # Arquivos LaTeX para relatórios gerais da equipe
```

# Setting Up Development Environment (Python)

- install python 3.12.4 https://www.python.org/downloads/release/python-3124/
    - make sure the python.exe is placed in the PATH during the installation wizard

- check that the installation was successful: open CMD and run `python -V`. It must show the version installed.
- clone / pull the repository
- go to folder containing project
- connect FUG and PUMP to computer. Make sure they show up in the Operating System's device manager.
- make sure the `setup.json` file has all the configurations used.

Now we need to do the following:
 * Create Pyhton virtual environment
 * Activate the virtual env
 * Install the packages in this virtual environment
 * Run the Jupyer Notebook inside this virtual environment
 
To do all those things, do the following:
- `python -m venv myEnv`
- cd to myEnv/Scripts (cd myEnv/Scripts/)
- `.\activate`
- cd back to project root folder (cd ../../)
- `pip install -r requirements.txt`
- check that all modules were installed: `pip freeze`
- choose the newly created virtual environment in the VS Code lower right corner
- run the program: `python main.py`
- to exit the virtual environment afterwards: `deactivate`

- & C:/dev/tesla/Data-Analysis/myEnv/Scripts/Activate.ps1


python -m pyflowchart test.py -o test.html



OU

cd myEnv/bin/
.\activate
cd ../../


# Procedimento para compilar os LaTeX localmente


## Configuração de ambiente

- Vá em https://www.latex-project.org/get/ 
- Clique em MikTex, na seção Windows, indo para https://miktex.org/download
- Faça download do MikTex para Windows 
- Salve em C:\Users\Usuario_01\AppData\Local\Programs\MiKTeX
- Instale a extensão LaTeX workshop no VS Code
- Instale o strawberry-perl-5.32.1.1-64bit.msi a partir de https://strawberryperl.com/
- Após a instalaçao, verifique o `perl` com
```
perl -v
```
Verifique o `PATH` do Windows caso não reconheça.
Talvez seja necessario fechar o VS Code e abrir de novo para o terminal integrado dele reconhecer o `perl`.
- Desative a extensão vscode-pdf para nao conflitar com a do latex.
- Rode o comando build com `ctrl + alt + B` (ou clica no icone verda da extensão no VS Code)
- Instale os packages que a extensão pedir que estão faltando.
- Nao deixe mostrar o dialog toda vez para cada instalação, deixe instalar todos packages de uma vez conforme a extensão precisar.
- Teste o PDF

- Usado a configuração `latex-workshop.latex.autoClean.run: OnBuilt` da extensão do VS Code que remove os arquivos auxiliares 
que são gerados após o build.


## Compilando localmente via CLI (sem o VS Code)

Compiling with BibTeX requires multiple steps (order matters):

    pdflatex main.tex

    bibtex main.aux

    pdflatex main.tex

    pdflatex main.tex

Ou cria um bash script para rodar isso automático.

Ou usa o VS que já faz tudo isso automático.

## Trabalho colaborativo

Use Git para fazer os relatórios em LaTeX de forma colaborativa com os outros membros, editando pelo VS Code e 
subindo o código para o repositório.
