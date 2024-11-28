if ((Get-Command "fuck").CommandType -eq "Function") {
	fuck @args;
	[Console]::ResetColor()
	exit
}

"First time use of fuckoff detected. "

if ((Get-Content $PROFILE -Raw -ErrorAction Ignore) -like "*fuckoff*") {
} else {
	"  - Adding fuckoff intialization to user `$PROFILE"
	$script = "`n` `niex `"`$(fuckoff --alias)`"";
	Write-Output $script | Add-Content $PROFILE
}

"  - Adding fuck() function to current session..."
iex "$($(fuckoff --alias).Replace("function fuck", "function global:fuck"))"

"  - Invoking fuck()`n"
fuck @args;
[Console]::ResetColor()
