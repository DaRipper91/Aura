; Aura Windows Installer (NSIS)
; Cyber-Monospace Aesthetic Setup

!include "MUI2.nsh"

; General
Name "Aura"
OutFile "dist\Aura_Setup_v1.0.5.exe"
InstallDir "$PROGRAMFILES64\Aura"
InstallDirRegKey HKCU "Software\Aura" ""
RequestExecutionLevel admin

; UI Settings
!define MUI_ABORTWARNING
; !define MUI_ICON "python\aura\ui\icon.ico" ; Add a .ico here for a custom icon
; !define MUI_UNICON "python\aura\ui\icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Add files from dist (PyInstaller output)
    File "dist\Aura_v1.0.5_Lite.exe"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Create Shortcuts
    CreateShortcut "$DESKTOP\Aura.lnk" "$INSTDIR\Aura_v1.0.5_Lite.exe"
    CreateDirectory "$SMPROGRAMS\Aura"
    CreateShortcut "$SMPROGRAMS\Aura\Aura.lnk" "$INSTDIR\Aura_v1.0.5_Lite.exe"
    CreateShortcut "$SMPROGRAMS\Aura\Uninstall Aura.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Registry keys for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Aura" "DisplayName" "Aura // Local AI Interchange"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Aura" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Aura" "DisplayIcon" "$INSTDIR\Aura_v1.0.5_Lite.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Aura" "Publisher" "DaRipper91"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\Aura_v1.0.5_Lite.exe"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$DESKTOP\Aura.lnk"
    Delete "$SMPROGRAMS\Aura\Aura.lnk"
    Delete "$SMPROGRAMS\Aura\Uninstall Aura.lnk"
    RMDir "$SMPROGRAMS\Aura"
    
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Aura"
SectionEnd
