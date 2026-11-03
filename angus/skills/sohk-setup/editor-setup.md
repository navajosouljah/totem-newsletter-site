# Editor connection reference

## Exact Premiere setup for the agent's technical reference

1. Ask the reader's operating system and which local AI client they already use. Check that Premiere is installed, licensed and opened locally. Keep original footage read-only and use a copy of the project for edits.
2. Install Node.js 20+ if absent. Install the **exact** package:
   `npm install -g adobe-premiere-pro-mcp`
3. Run `premiere-pro-mcp --install-cep`, then `premiere-pro-mcp --doctor`. Both flags were verified in this run's CLI help. The installer changes local Adobe CEP configuration and supported client configuration; present that normal setup clearly.
4. Restart Premiere. Open **Window → Extensions → MCP Bridge (CEP)**. Use the directory printed by the installer. The current panel automatically starts; if stopped, use **Start Bridge**. The source's HTML includes the exact labels.
5. Register a local stdio server named `premiere-pro` using command `premiere-pro-mcp`. This is not a hosted MCP URL and needs no vendor API key. The official Claude Desktop release bundle can be installed from this repository's GitHub Releases instead; the package installer supports Claude Desktop configuration.
6. Ask the client to run `verify_premiere_connection`. For a probe that never launches the app, set `launchIfNeeded:false`. A failure returns a `nextStep`; follow it instead of repeatedly trying editing calls.
7. Discover tools through `search_tools`, get exact schemas through `get_tool_schema`, then call `invoke_tool`. Never assume 283 editing tools appear at top level.
8. Use source-linked selections. A timeline insert supports `sequenceId, projectItemId, trackIndex, time, sourceInPoint, sourceOutPoint`; in/out are seconds and must be supplied together. Batch insertion returns placed/failed counts and can be partial.
9. Create one sequence per hook and version. Use `create_sequence_from_clips` or duplicate a known correctly configured 1080×1920 sequence; `create_sequence` needs a specific installed sequence preset, and source warns that its frame-rate argument is not a reliable configuration path. Read back dimensions and rate.
10. Discover an actual installed `.epr` with `get_encoder_presets` (user preset discovery is not a promise that all factory presets are found). Set `export_sequence` with sequence ID, absolute output path, and preset path/name. After export, check the real file with ffprobe and play its beginning, each join and ending. Queue acceptance is not a completed MP4.

Sources: https://premiere-mcp.com/docs/ ; https://github.com/hetpatel-11/Adobe_Premiere_Pro_MCP ; downloaded package `dist/tools/definitions/discovery.js`, `timeline.js`, `sequence.js`, `export.js`, `cep-plugin/index.html`. No live panel screenshot was captured because Premiere is absent here. Existing B-roll `S19-alt-mcp-tool-reference.png` is a tool reference, not proof of ten exported sequences.

## Descript connector verification

Official connector docs: https://help.descript.com/api-and-mcp/mcp and https://help.descript.com/account-and-app-settings/app-settings .
Directory connector first. Custom URL: `https://api.descript.com/v2/mcp`; login/Drive authorization, no API token needed for MCP. In Descript Settings, the **Descript MCP** section provides connect buttons. Current docs expose imports, Underlord edits, transcript exports, project search and publishing.

The live connector in this session exposes `import_media`, `prompt_project_agent`, `export_transcript`, `export_timeline`, `get_project`, `list_projects`, `publish_project`, `wait_for_job` and others. A minimal `list_projects({limit:1})` succeeded on 2026-10-30. This proves connection, not editing/export. No Descript project was changed.

## FFmpeg path and smoke-check plan

FFmpeg 8.0.1 is installed here; `ffmpeg -version` succeeded. An agent can install an OS build linked from https://ffmpeg.org/download.html and check `ffmpeg -version` / `ffprobe -version`. No account or connector is needed; the agent needs permission to run local commands and access the footage.

For accurate trims, decode/re-encode; stream-copy seeking may cut on nearby keyframes. Give the agent source time ranges and verify audio at joins. Derive crop coordinates from actual speaker positions; do not force a center crop that removes the speaker. An exported MP4 and its source-to-output time map are the deliverables. Native subtitles should be checked against the audio, not blindly copied from auto-captions.

