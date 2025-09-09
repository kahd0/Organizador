Organizador de Atividades

Um aplicativo desktop para gerenciar atividades e requisitos, com funcionalidades de criação, edição e finalização de tarefas. A aplicação organiza automaticamente pastas e gera arquivos ZIP ao finalizar atividades.

Funcionalidades

Criar novas atividades, com prazo e tipo.

Editar atividades existentes.

Finalizar atividades, gerando ZIP automaticamente.

Atualização automática do status:

Atrasado: atividades com prazo expirado.

Finalizado: atividades concluídas.

Organização de pastas de requisitos.

Exclusão segura de pastas usando a lixeira do sistema (send2trash).

Suporte a pastas e subpastas para cada requisito.

Ícones de status visuais no sistema.

Estrutura de Pastas
Organizador/
├─ main.py
├─ config.py
├─ paths.py
├─ storage.py
├─ utils/
│  └─ fs.py
└─ ui/
   ├─ gui_utils.py
   ├─ tray_app.py
   └─ windows/
      ├─ config_window.py
      ├─ controle_atividades.py
      ├─ editar_movimentacao.py
      └─ nova_atividade.py

Requisitos

Python 3.12+

PySide6

send2trash

pyinstaller (para gerar o executável)

Instale as dependências:

pip install pyside6 send2trash pyinstaller

Executando
Diretamente do código
python main.py

Como executável (Windows)

O executável é gerado usando PyInstaller:

pyinstaller --onefile --windowed `
    --hidden-import=PySide6 `
    --hidden-import=send2trash `
    --add-data "ui;ui" `
    --add-data "utils;utils" `
    --add-data "config.py;." `
    main.py


O .exe gerado estará na pasta dist/.

Configuração

As pastas padrão são configuradas em config.py:

DEFAULT_PENDING = Path(r"C:\Atividades\Pendentes")
DEFAULT_COMPLETED = Path(r"C:\Atividades\Finalizadas")


Você pode alterar esses caminhos no arquivo config_data.json criado na primeira execução.

Observações

Atividades sem arquivos em uma pasta de requisito vazia são removidas automaticamente.

Pastas com qualquer arquivo são mantidas, mesmo sem JSON.

Ao finalizar uma atividade, a pasta original é movida para a lixeira e um ZIP é criado na pasta de finalizadas.
