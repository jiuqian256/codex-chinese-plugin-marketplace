/*
  Export a 3ds Max scene to OBJ and FBX.
  Required command-line parameters:
    -mxsString "sourceFile:<absolute .max path>"
    -mxsString "outputFolder:<absolute output directory>"
*/

clearListener()

fn codexGetArg argName =
(
    try (maxOps.mxsCmdLineArgs[argName]) catch (undefined)
)

sourceFile = codexGetArg #sourceFile
outputFolder = codexGetArg #outputFolder

try
(
    if sourceFile == undefined or outputFolder == undefined do throw "Specify sourceFile and outputFolder via -mxsString."
    if not doesFileExist sourceFile do throw ("Source file is missing: " + sourceFile)
    if not doesDirectoryExist outputFolder do makeDir outputFolder all:true

    baseName = getFilenameFile sourceFile
    objFile = outputFolder + "\\" + baseName + ".obj"
    fbxFile = outputFolder + "\\" + baseName + ".fbx"

    loadMaxFile sourceFile quiet:true useFileUnits:true
    exportFile objFile #noPrompt selectedOnly:false
    exportFile fbxFile #noPrompt selectedOnly:false
    format "CODEX_EXPORT_SUCCESS: OBJ=% FBX=%\n" objFile fbxFile
)
catch
(
    format "CODEX_EXPORT_ERROR: %\n" (getCurrentException())
)

quitMax #noPrompt
