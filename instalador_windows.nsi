; Script de instalação para Gorillas 3D War (Windows)
; Requer NSIS (Nullsoft Scriptable Install System)

; Configurações do instalador
!define APPNAME "Gorillas 3D War"
!define COMPANYNAME "Gorillas3DWar"
!define DESCRIPTION "Um jogo de artilharia 3D inspirado no clássico Gorillas"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define ABOUTURL "https://github.com/gorillas3dwar"

; Nome do arquivo de saída
OutFile "Gorillas3DWar_Setup.exe"

; Pasta de instalação padrão
InstallDir "$PROGRAMFILES\${APPNAME}"

; Solicitar privilégios de administrador
RequestExecutionLevel admin

; Interface
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "textures\icon.ico"
!define MUI_UNICON "textures\icon.ico"

; Páginas do instalador
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Páginas de desinstalação
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Configurações de idioma
!insertmacro MUI_LANGUAGE "Portuguese"

; Seção de instalação principal
Section "Instalar ${APPNAME}" SecInstall
    SetOutPath "$INSTDIR"
    
    ; Arquivos a serem instalados
    File /r "dist\Gorillas3DWar\*.*"
    
    ; Criar atalho no menu iniciar
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\iniciar.bat" "" "$INSTDIR\textures\icon.ico"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk" "$INSTDIR\uninstall.exe"
    
    ; Criar atalho na área de trabalho
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\iniciar.bat" "" "$INSTDIR\textures\icon.ico"
    
    ; Criar desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Adicionar informações ao Adicionar/Remover Programas
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\textures\icon.ico$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
SectionEnd

; Seção de verificação/instalação do Python
Section "Instalar Python e Dependências" SecPython
    ; Verifica se o Python já está instalado
    nsExec::ExecToStack 'python --version'
    Pop $0
    Pop $1
    
    ${If} $0 != 0
        MessageBox MB_YESNO "Python não detectado. Deseja baixar e instalar o Python 3.9?" IDYES installPython IDNO skipPython
        
        installPython:
            ; Download e instalação do Python
            inetc::get "https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe" "$TEMP\python-installer.exe"
            ExecWait '"$TEMP\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1'
            Delete "$TEMP\python-installer.exe"
            
            ; Instala o Panda3D
            ExecWait 'pip install panda3d'
            Goto pythonDone
            
        skipPython:
            MessageBox MB_OK "Atenção: O jogo requer Python 3.7+ e Panda3D para funcionar. Por favor, instale-os manualmente."
    ${Else}
        ; Python está instalado, verifica o Panda3D
        nsExec::ExecToStack 'pip show panda3d'
        Pop $0
        Pop $1
        
        ${If} $0 != 0
            MessageBox MB_YESNO "Panda3D não detectado. Deseja instalar o Panda3D?" IDYES installPanda IDNO skipPanda
            
            installPanda:
                ExecWait 'pip install panda3d'
                Goto pandaDone
                
            skipPanda:
                MessageBox MB_OK "Atenção: O jogo requer Panda3D para funcionar. Por favor, instale-o manualmente com 'pip install panda3d'."
                
            pandaDone:
        ${EndIf}
    ${EndIf}
    
    pythonDone:
SectionEnd

; Seção de desinstalação
Section "Uninstall"
    ; Remove arquivos e pastas
    RMDir /r "$INSTDIR\*.*"
    RMDir "$INSTDIR"
    
    ; Remove atalhos
    Delete "$SMPROGRAMS\${APPNAME}\*.*"
    RMDir "$SMPROGRAMS\${APPNAME}"
    Delete "$DESKTOP\${APPNAME}.lnk"
    
    ; Remove entradas de registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
