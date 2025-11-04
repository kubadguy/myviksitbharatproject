📂 Project Setup and Initialization Documentation
-------------------------------------------------

This guide outlines the commands necessary to clone and run the project repository across different operating systems.

### 🌐 Prerequisites

The following software must be installed on your system before running the commands:

*   **Git:** Version control system (required for cloning the repository).
    
*   **Python 3:** The programming language interpreter (required for running the application).
    

### 🐧 UNIX, LINUX, MacOS, or Unix-Based Systems

These commands are executed in a standard shell environment (Bash, Zsh, etc.).

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # 1. Check the installed Git version  git --version  # 2. Set an environment variable for the repository link (No spaces around '=')  export CODE_LINK=https://github.com/kubadguy/myviksitbharatproject.git  # 3. Change the current directory to the user's home directory  cd ~  # 4. Clone the repository using the environment variable  git clone $CODE_LINK  # 5. Navigate into the newly cloned project directory  cd myviksitbharatproject   `

### 💻 Windows Command Prompt (CMD)

These commands are executed in the **Windows Command Prompt (CMD)** terminal.

DOS

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   REM 1. Check the installed Git version  git --version  REM 2. Set a temporary environment variable for the repository link  set CODE_LINK=https://github.com/kubadguy/myviksitbharatproject.git  REM 3. Change the current directory to the user's home directory  cd %USERPROFILE%  REM 4. Clone the repository using the environment variable  git clone %CODE_LINK%  REM 5. Navigate into the newly cloned project directory  cd myviksitbharatproject   `

### 🚀 Windows PowerShell

These commands are executed in the **Windows PowerShell** terminal.

PowerShell

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # 1. Check the installed Git version  git --version  # 2. Set a temporary environment variable for the repository link  $env:CODE_LINK="https://github.com/kubadguy/myviksitbharatproject.git"  # 3. Change the current directory to the user's home directory  cd $HOME  # 4. Clone the repository using the environment variable  git clone $env:CODE_LINK  # 5. Navigate into the newly cloned project directory  cd myviksitbharatproject   `

### 🖼️ Running the GUI

Once you have successfully navigated into the myviksitbharatproject directory, use the following command to run the graphical user interface (GUI) of the application.

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python3 src gui   `

**Note:** The exact command to run the application (python3 src gui) assumes that your main executable script is located at src/gui.py or similar, and that python3 is the correct command to execute Python 3 on your system.