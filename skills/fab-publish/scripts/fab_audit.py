#!/usr/bin/env python3
"""fab_audit.py - read-only pre-submission audit for Fab (fab.com) products.

Usage:
    python fab_audit.py <path> [--json]     audit a folder, .zip, or .unitypackage
    python fab_audit.py --selftest          build temporary fixtures and assert results

It never modifies, moves or deletes anything. Python 3.8+ standard library only.
Checks are paraphrased from Fab's public requirements (docs snapshot 2026-11-18);
every result carries a source link. Not affiliated with Epic Games or Unity.
"""
import json
import os
import re
import struct
import sys
import tarfile
import tempfile
import wave
import zipfile
from datetime import date

# ---------------------------------------------------------------- sources
TR = "https://www.fab.com/o/technical-requirements"
AFF = "https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab"
PUB = "https://dev.epicgames.com/documentation/fab/publishing-assets-for-sale-or-free-download-in-fab"
UEFN_DOC = "https://dev.epicgames.com/documentation/fab/upload-unreal-editor-for-fortnite-source-to-fab"
UNSUP = "https://support.fab.com/s/article/Unsupported-File-Types-on-Fab?language=en_US"
TROUBLE = "https://support.fab.com/s/article/Fab-Plugin-Compilation-Troubleshooting?language=en_US"
DA = "https://www.fab.com/distribution-agreement"
UAS = "https://assetstore.unity.com/publishing/submission-guidelines"


def tr(n):
    return "%s (TR %s)" % (TR, n)


def uas(n):
    return "%s (Unity %s)" % (UAS, n)


# ---------------------------------------------------------------- constants
FORBIDDEN_EXT = {".exe", ".msi", ".iso", ".dmg", ".0", ".rar", ".7z", ".z", ".gz", ".tar",
                 ".tgz", ".bz2", ".xz", ".apk", ".app", ".bat", ".cmd", ".com", ".scr"}
FORBIDDEN_OK = {".unitypackage.gz"}  # top-level Unity format Fab accepts
LOCAL_DIRS = {"binaries", "intermediate", "saved", "deriveddatacache", "build", ".vs", ".idea",
              ".git", ".svn", "__pycache__"}
UNITY_LOCAL_DIRS = {"library", "temp", "obj", "logs", "usersettings", ".vs", ".idea", ".git"}
VAGUE_NAME = re.compile(r"^(new_?folder\d*|new folder\d*|assets|untitled\d*|folder\d*|temp|tmp|stuff|misc|test\d*)$", re.I)
UE_NAME_OK = re.compile(r"^[A-Za-z0-9_]+$")
MODULE_TYPES = {"Runtime", "RuntimeNoCommandlet", "RuntimeAndProgram", "CookedOnly", "UncookedOnly",
                "Developer", "DeveloperTool", "Editor", "EditorNoCommandlet", "EditorAndProgram",
                "Program", "ServerOnly", "ClientOnly", "ClientOnlyNoCommandlet"}
LOADING_PHASES = {"EarliestPossible", "PostConfigInit", "PostSplashScreen", "PreEarlyLoadingScreen",
                  "PreLoadingScreen", "PreDefault", "Default", "PostDefault", "PostEngineInit", "None"}
BAD_PLATFORMS = {"HTML5"}
PLUGIN_TOP_OK = {"config", "content", "resources", "source", "shaders"}
BINARY_LIB_EXT = {".dll", ".lib", ".so", ".a", ".dylib", ".pdb"}
PLACEHOLDER_EXT = {".uasset", ".umap", ".fbx", ".obj", ".glb", ".blend", ".prefab", ".unity", ".wav"}
DCC_EXT = {".fbx", ".obj", ".glb", ".gltf", ".usd", ".usda", ".usdc", ".usdz", ".blend", ".max",
           ".ma", ".mb", ".c4d", ".dae", ".abc"}
UNITY_MESH_OK = {".fbx", ".dae", ".abc", ".obj"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tga"}
AUDIO_LOSSLESS = {".wav", ".aiff", ".aif", ".flac"}
AUDIO_LOSSY = {".mp3", ".ogg"}
TEXT_EXT = {".h", ".hpp", ".cpp", ".c", ".cc", ".inl", ".cs", ".ini", ".json", ".uplugin", ".uproject",
            ".py", ".md", ".txt", ".usf", ".ush", ".verse", ".asmdef", ".asmref", ".mtl", ".gltf",
            ".xml", ".yaml", ".yml", ".shader", ".hlsl", ".cginc", ".compute", ".uss", ".uxml"}
ABS_PATH = re.compile(r"([A-Za-z]:[\\/]{1,2}(Users|Documents and Settings|Program Files)[\\/]|/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/)")
COPYLEFT = re.compile(r"(GNU (Affero |Lesser )?General Public License|SPDX-License-Identifier:\s*(A?GPL|LGPL|EPL|MS-PL|CC-BY-SA)|Creative Commons Attribution-ShareAlike|Eclipse Public License|Microsoft Public License)", re.I)
LICENSE_FILE = re.compile(r"^(license|licence|copying|notice|third[ _-]?party[ _-]?notices?)([._ -].*)?$|\.tps$", re.I)
DOC_FILE = re.compile(r"(readme|docs?|documentation|manual|guide|getting[_ -]?started|tutorial)", re.I)
DOC_EXT = {".md", ".txt", ".pdf", ".html", ".htm", ".rtf"}
UNITY_SPECIAL_ROOT = {"editor default resources", "gizmos", "streamingassets", "plugins", "standard assets"}
MAX_TEXT = 2 * 1024 * 1024
GB = 1024 ** 3

STATUS_ICON = {"pass": "\u2705", "fail": "\u274c", "ask": "\u2753"}


# ---------------------------------------------------------------- trees
class Tree:
    """Uniform read-only view of a folder, a .zip or a .unitypackage: {relpath: size}."""

    def __init__(self, path):
        self.path = path
        self.files = {}
        self.kind = "dir"
        self.zip_info = None
        self._src = {}
        low = path.lower()
        if os.path.isdir(path):
            for dp, dns, fns in os.walk(path):
                dns[:] = [d for d in dns if d not in ("node_modules",)]
                for fn in fns:
                    full = os.path.join(dp, fn)
                    rel = os.path.relpath(full, path).replace(os.sep, "/")
                    try:
                        self.files[rel] = os.path.getsize(full)
                    except OSError:
                        pass
                    self._src[rel] = full
        elif low.endswith(".zip"):
            self.kind = "zip"
            self._zf = zipfile.ZipFile(path)
            self.zip_info = self._zf.infolist()
            for zi in self.zip_info:
                if not zi.is_dir():
                    self.files[zi.filename] = zi.file_size
        elif low.endswith(".unitypackage") or low.endswith(".unitypackage.gz"):
            self.kind = "unitypackage"
            self._tf = tarfile.open(path, "r:*")
            members = {m.name.lstrip("./"): m for m in self._tf.getmembers()}
            for name, m in members.items():
                if name.endswith("/pathname"):
                    guid = name[:-len("/pathname")]
                    rel = self._tf.extractfile(m).read().decode("utf-8", "replace").splitlines()[0].strip()
                    asset = members.get(guid + "/asset")
                    if asset is not None:
                        self.files[rel] = asset.size
                        self._src[rel] = asset
                    else:
                        self.files.setdefault(rel.rstrip("/") + "/", 0)  # folder entry
        else:
            self.kind = "file"
            self.files[os.path.basename(path)] = os.path.getsize(path)
            self._src[os.path.basename(path)] = path

    def read(self, rel, limit=MAX_TEXT):
        try:
            if self.kind == "zip":
                with self._zf.open(rel) as f:
                    return f.read(limit)
            if self.kind == "unitypackage":
                f = self._tf.extractfile(self._src[rel])
                return f.read(limit) if f else b""
            with open(self._src[rel], "rb") as f:
                return f.read(limit)
        except (KeyError, OSError, RuntimeError, zipfile.BadZipFile):
            return b""

    def text(self, rel):
        return self.read(rel).decode("utf-8-sig", "replace")

    def under(self, root):
        """Files under root ('' = everything), relative to root."""
        if not root:
            return dict(self.files)
        p = root.rstrip("/") + "/"
        return {k[len(p):]: v for k, v in self.files.items() if k.startswith(p)}

    def dirs_under(self, root):
        out = set()
        for rel in self.under(root):
            parts = rel.split("/")[:-1]
            for i in range(len(parts)):
                out.add("/".join(parts[:i + 1]))
        return out


def join(root, rel):
    return rel if not root else root.rstrip("/") + "/" + rel


def ext_of(name):
    n = name.lower()
    if n.endswith(".unitypackage.gz"):
        return ".unitypackage.gz"
    return os.path.splitext(n)[1]


# ---------------------------------------------------------------- report
class Report:
    def __init__(self, path):
        self.path = path
        self.detected = []
        self.facts = {}
        self.results = []

    def add(self, id_, category, status, message, source, severity="blocker"):
        self.results.append({"id": id_, "category": category, "status": status,
                             "severity": severity if status != "pass" else "",
                             "message": message, "source": source})

    def ok(self, id_, cat, msg, src):
        self.add(id_, cat, "pass", msg, src)

    def fail(self, id_, cat, msg, src, severity="blocker"):
        self.add(id_, cat, "fail", msg, src, severity)

    def ask(self, id_, cat, msg, src, severity="review risk"):
        self.add(id_, cat, "ask", msg, src, severity)

    def check(self, id_, cat, bad, ok_msg, bad_msg, src, severity="blocker", sample=None):
        if bad:
            if sample:
                bad_msg += ": " + ", ".join(sample[:5]) + (" (+%d more)" % (len(sample) - 5) if len(sample) > 5 else "")
            self.fail(id_, cat, bad_msg, src, severity)
        else:
            self.ok(id_, cat, ok_msg, src)

    def to_json(self):
        return {"path": self.path, "detected": self.detected, "facts": self.facts,
                "results": self.results, "summary": self.summary()}

    def summary(self):
        s = {"pass": 0, "fail": 0, "ask": 0, "blockers": 0}
        for r in self.results:
            s[r["status"]] += 1
            if r["status"] == "fail" and r["severity"] == "blocker":
                s["blockers"] += 1
        return s

    def render(self):
        out = ["Fab pre-submission audit: %s" % self.path,
               "Detected: %s" % (", ".join("%s (%s)" % (d["type"], d["root"] or ".") for d in self.detected) or "nothing recognised"),
               ""]
        if self.facts:
            out.append("Facts")
            for k, v in self.facts.items():
                out.append("  %s: %s" % (k, v if not isinstance(v, (list, dict)) else json.dumps(v)))
            out.append("")
        cats = []
        for r in self.results:
            if r["category"] not in cats:
                cats.append(r["category"])
        for c in cats:
            out.append(c)
            for r in self.results:
                if r["category"] != c:
                    continue
                sev = " [%s]" % r["severity"] if r["severity"] else ""
                out.append("  %s %s%s - %s" % (STATUS_ICON[r["status"]], r["id"], sev, r["message"]))
                if r["status"] != "pass":
                    out.append("      source: %s" % r["source"])
            out.append("")
        s = self.summary()
        out.append("Summary: %d pass, %d fail (%d blockers), %d need input. Automated checks only; "
                   "manual and listing checks are in the skill references." % (s["pass"], s["fail"], s["blockers"], s["ask"]))
        return "\n".join(out)


# ---------------------------------------------------------------- detection
def detect(tree):
    found = []
    files = tree.files
    names = list(files)
    if tree.kind == "unitypackage":
        return [{"type": "unity-package", "root": ""}]
    for n in names:
        e = ext_of(n)
        root = os.path.dirname(n)
        if e == ".uplugin":
            found.append({"type": "ue-plugin", "root": root})
        elif e == ".uproject":
            found.append({"type": "ue-project", "root": root})
        elif e == ".uefnproject":
            found.append({"type": "uefn", "root": root})
        elif e == ".mhpkg":
            found.append({"type": "metahuman", "root": root})
        elif e in (".unitypackage", ".unitypackage.gz"):
            found.append({"type": "unity-package-file", "root": n})
        elif os.path.basename(n) == "package.json":
            try:
                pj = json.loads(tree.text(n))
            except ValueError:
                pj = {}
            if isinstance(pj, dict) and ("unity" in pj or re.match(r"^com\.[a-z0-9-]+\.", str(pj.get("name", "")))):
                found.append({"type": "unity-upm", "root": root})
    roots = {}
    for n in names:
        parts = n.split("/")
        if "Assets" in parts:
            i = parts.index("Assets")
            roots.setdefault("/".join(parts[:i]), True)
    claimed = [d["root"] for d in found if d["type"] in ("ue-plugin", "ue-project", "uefn", "unity-upm")]
    for r in roots:
        if any(r == c or r.startswith(c + "/") or (c and (c + "/").startswith(r + "/")) or (not r and c) for c in claimed):
            continue
        has_ps = any(k.startswith(join(r, "ProjectSettings/")) for k in names)
        found.append({"type": "unity-project" if has_ps else "unity-assets", "root": r})
    if not found:
        loose = {ext_of(n) for n in names}
        if loose & DCC_EXT:
            found.append({"type": "dcc-3d", "root": ""})
        if loose & (AUDIO_LOSSLESS | AUDIO_LOSSY):
            found.append({"type": "audio-files", "root": ""})
        if loose & {".hdr", ".exr"}:
            found.append({"type": "hdri-files", "root": ""})
    return found


# ---------------------------------------------------------------- generic checks
def check_package(tree, rep, types):
    cat = "Package and archive"
    if tree.kind == "zip":
        size = os.path.getsize(tree.path)
        rep.facts["zip_size_mb"] = round(size / 1024 ** 2, 1)
        enc = [z.filename for z in tree.zip_info if z.flag_bits & 0x1]
        rep.check("zip.encrypted", cat, enc, "Zip is not password-protected",
                  "Zip has encrypted entries; Fab cannot scan an archive it cannot open", AFF + " (Unreal Engine Project Format)", sample=enc)
        z64 = any(z.file_size > 0xFFFFFFFF or z.compress_size > 0xFFFFFFFF or z.header_offset > 0xFFFFFFFF
                  or b"\x01\x00" == z.extra[:2] for z in tree.zip_info) or len(tree.zip_info) > 65535
        rep.check("zip.zip64", cat, z64, "Zip does not use zip64 extensions",
                  "Zip uses zip64, which Fab lists as unsupported; re-zip below 4 GB per file / 65,535 entries or split the product", UNSUP, severity="review risk")
        meth = sorted({z.compress_type for z in tree.zip_info} - {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED})
        rep.check("zip.compression", cat, meth, "Zip uses standard Deflate/Stored compression",
                  "Zip uses non-standard compression methods %s; re-zip with Deflate so Fab's scanner can read it" % meth, AFF, severity="review risk")
    else:
        size = sum(v for k, v in tree.files.items() if not any(p.lower() in LOCAL_DIRS for p in k.split("/")[:-1]))
        rep.facts["package_size_mb_excluding_local_folders"] = round(size / 1024 ** 2, 1)
    limit, label = 6 * GB, "6 GB (non-engine formats; Unity Asset Store limit)"
    tset = {t["type"] for t in types}
    if tset & {"ue-plugin", "ue-project", "uefn"}:
        limit, label = 15 * GB, "15 GB (Unreal; larger needs Fab's review)"
    if "unity-upm" in tset:
        limit, label = 700 * 1024 ** 2, "700 MB (UPM package)"
    if "metahuman" in tset:
        limit, label = int(1.5 * GB), "1.5 GB (.mhpkg)"
    rep.check("package.size", cat, size > limit, "Size %.1f MB is under %s" % (size / 1024 ** 2, label),
              "Size %.1f MB exceeds %s" % (size / 1024 ** 2, label), AFF + " (File Format Requirements)", severity="review risk")
    bad = [n for n in tree.files if ext_of(n) in FORBIDDEN_EXT and ext_of(n) not in FORBIDDEN_OK]
    rep.check("files.forbidden", cat, bad, "No executables, installers or non-zip archives",
              "Forbidden file types (executables/installers/non-zip archives) found", tr("2.2") + "; " + UNSUP, sample=bad)
    nested = [n for n in tree.files if ext_of(n) == ".zip"]
    if nested and not tset & {"unity-project", "unity-assets", "unity-package"}:
        rep.ask("files.nested_zip", cat, "Zip files inside the package (%s); confirm they are needed and not nested product archives" % ", ".join(nested[:3]), AFF)
    uploads = [t for t in types if t["type"] in ("ue-plugin", "ue-project", "uefn", "metahuman")]
    kinds = {}
    for t in uploads:
        kinds.setdefault(t["type"], []).append(t["root"] or ".")
    multi = [k for k, v in kinds.items() if len(v) > 1]
    rep.check("package.single", cat, multi, "One product per upload",
              "More than one %s in this upload (%s); each zip must hold exactly one project or plugin" % (
                  "/".join(multi), "; ".join(sum((kinds[k] for k in multi), []))), tr("4.2.1.a") + "; " + AFF, sample=None)
    # ponytail: size heuristic; real engine/DCC assets are never this small, so these are placeholders or broken saves
    stub = [n for n, s in tree.files.items() if ext_of(n) in PLACEHOLDER_EXT and s < 512]
    rep.check("files.placeholder", cat, stub, "No placeholder-sized asset files",
              "Asset files under 512 bytes look like placeholders or broken saves; re-save or export them for real", tr("1.1.a"),
              severity="review risk", sample=stub)


def check_text_hygiene(tree, rep, root, cat="Code and text files"):
    files = tree.under(root)
    abs_hits, gpl_hits = [], []
    for rel, size in files.items():
        if ext_of(rel) not in TEXT_EXT or size > MAX_TEXT:
            continue
        t = tree.text(join(root, rel))
        if ABS_PATH.search(t):
            abs_hits.append(rel)
        if COPYLEFT.search(t) and not LICENSE_FILE.match(os.path.basename(rel)):
            gpl_hits.append(rel)
    rep.check("text.absolute_paths", cat, abs_hits, "No developer-machine absolute paths in text files",
              "Absolute or user-profile paths found (break on buyers' machines)", AFF + " (Python Scripts: no hardcoded paths)",
              severity="review risk", sample=abs_hits)
    rep.check("legal.copyleft", "Legal and third-party", gpl_hits, "No GPL/LGPL/EPL/MS-PL/CC-BY-SA licence text in source files",
              "Copyleft licence text found; Fab's agreement bars code under licences that would override the Fab EULA", DA + " (s.3c, 3f.vi)", sample=gpl_hits)


def check_leftovers(tree, rep, root, local_dirs, src, cat="Structure and naming"):
    dirs = tree.dirs_under(root)
    hits = sorted({d for d in dirs if d.split("/")[-1].lower() in local_dirs
                   and not any(p.lower() in local_dirs for p in d.split("/")[:-1])})
    hits = [h for h in hits if not h.lower().startswith("source/thirdparty")]
    rep.check("structure.local_folders", cat, hits, "No local/build/cache folders (Binaries, Intermediate, Saved, Library, Temp, ...)",
              "Local or build folders must be removed before zipping", src, sample=hits)


def check_names_paths(tree, rep, root, scope, limit, src_names, src_len, top_name, ue_names=True, check_len=True):
    """scope: path prefix under root whose files are checked; length measured from top_name."""
    cat = "Structure and naming"
    files = [f for f in tree.under(root) if f.startswith(scope)]
    if ue_names:
        bad = sorted({p for f in files for p in f[len(scope):].split("/")
                      if not UE_NAME_OK.match(os.path.splitext(p)[0] if "." in p else p)})
        rep.check("naming.charset", cat, bad, "File and folder names use only English letters, digits and underscores",
                  "Names with spaces, hyphens or non-English characters", src_names, severity="review risk", sample=bad)
    vague = sorted({p for f in files for p in f[len(scope):].split("/")[:-1] if VAGUE_NAME.match(p)})
    rep.check("naming.vague", cat, vague, "No vaguely named folders (Assets, NewFolder, ...)",
              "Vague folder names; rename to say what they contain", src_names, severity="review risk", sample=vague)
    if not check_len:
        return
    too_long = [top_name + "/" + f[len(scope):] if top_name else f for f in files]
    too_long = [p for p in too_long if len(p) > limit]
    rep.check("paths.length", cat, too_long, "All paths are %d characters or less (measured from %s)" % (limit, top_name or "root"),
              "Paths longer than %d characters" % limit, src_len, sample=too_long)


def image_size(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            m = data[i + 1]
            if m in (0xC0, 0xC1, 0xC2, 0xC3):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
        return None
    if len(data) >= 18 and data[2] in (1, 2, 3, 9, 10, 11):
        return struct.unpack("<HH", data[12:16])
    return None


def check_images(tree, rep, root, max_dim, src):
    cat = "Textures and images"
    imgs = [f for f in tree.under(root) if ext_of(f) in IMAGE_EXT]
    if not imgs:
        return
    too_big, not_pow2, sizes = [], [], {}
    for f in imgs:
        wh = image_size(tree.read(join(root, f), 65536))
        if not wh:
            continue
        w, h = wh
        sizes["%dx%d" % (w, h)] = sizes.get("%dx%d" % (w, h), 0) + 1
        if max(w, h) > max_dim:
            too_big.append("%s (%dx%d)" % (f, w, h))
        if (w & (w - 1)) or (h & (h - 1)):
            not_pow2.append("%s (%dx%d)" % (f, w, h))
    rep.facts["image_sizes"] = sizes
    rep.check("textures.max_size", cat, too_big, "No image larger than %d px in either dimension" % max_dim,
              "Images over %d px" % max_dim, src, sample=too_big)
    if not_pow2:
        rep.ask("textures.power_of_two", cat, "Non power-of-two images (fine for UI/no-mip textures, otherwise resize): "
                + ", ".join(not_pow2[:5]), src, severity="recommended")
    else:
        rep.ok("textures.power_of_two", cat, "All image dimensions are powers of two", src)


def check_audio(tree, rep, root, unity=False):
    cat = "Audio"
    files = tree.under(root)
    wavs = [f for f in files if ext_of(f) == ".wav"]
    lossy = [f for f in files if ext_of(f) in AUDIO_LOSSY]
    if not wavs and not lossy:
        return
    stats = {}
    hot = []
    for f in wavs[:200]:
        data = tree.read(join(root, f), 64 * 1024 * 1024)
        try:
            import io
            w = wave.open(io.BytesIO(data))
            sr, ch, sw, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
            key = "%d Hz / %d-bit / %dch" % (sr, sw * 8, ch)
            stats[key] = stats.get(key, 0) + 1
            if sw == 2:
                import array
                a = array.array("h", w.readframes(n))
                if sys.byteorder == "big":
                    a.byteswap()
                peak = max((abs(x) for x in a), default=0)
                if peak >= 31770:  # about -0.3 dBFS
                    hot.append(f)
        except (wave.Error, EOFError, ValueError):
            stats["unreadable"] = stats.get("unreadable", 0) + 1
    rep.facts["audio_formats"] = stats
    rep.facts["audio_file_count"] = len(wavs) + len(lossy)
    if unity:
        rep.check("audio.peak", cat, hot, "No 16-bit WAV peaks above about -0.3 dBFS",
                  "WAV files peaking above -0.3 dBFS (clipping risk)", uas("2.7.b"), severity="review risk", sample=hot)
        lossless = [f for f in files if ext_of(f) in AUDIO_LOSSLESS]
        if lossy and not lossless:
            rep.fail("audio.lossless", cat, "Only lossy audio (.mp3/.ogg); audio products need lossless files (.wav/.aiff/.flac)",
                     uas("2.7.c"), severity="review risk")
    elif lossy:
        rep.ask("audio.wav_import", cat, "Lossy audio files present (%s); Unreal audio should be imported from .wav" % ", ".join(lossy[:3]),
                tr("4.3.4.a"))


# ---------------------------------------------------------------- Unreal: plugin
def check_ue_plugin(tree, rep, root):
    cat = "Plugin descriptor (.uplugin)"
    files = tree.under(root)
    top = os.path.basename(root) or os.path.splitext(os.path.basename(tree.path))[0]
    uplugins = [f for f in files if "/" not in f and f.endswith(".uplugin")]
    up = uplugins[0] if uplugins else None
    data = None
    try:
        data = json.loads(tree.text(join(root, up)))
        rep.ok("uplugin.json", cat, "%s is valid JSON" % up, TROUBLE)
    except ValueError as e:
        rep.fail("uplugin.json", cat, "%s is not valid JSON (%s); the build farm fails with a parse error" % (up, e), TROUBLE)
    rep.facts["plugin"] = up
    if isinstance(data, dict):
        for k in ("FriendlyName", "VersionName", "Version", "EngineVersion", "Description", "Category", "CreatedBy",
                  "CreatedByURL", "DocsURL", "SupportURL", "FabURL", "MarketplaceURL", "CanContainContent"):
            if k in data:
                rep.facts["uplugin." + k] = data[k]
        ev = str(data.get("EngineVersion", ""))
        if not ev:
            rep.fail("uplugin.engine_version", cat, 'Missing "EngineVersion" (for example "5.6.0")', tr("4.3.6.a"))
        elif not re.match(r"^\d+\.\d+\.0$", ev):
            rep.fail("uplugin.engine_version", cat, 'EngineVersion "%s" should name a major version as X.Y.0' % ev, tr("4.3.6.a"))
        else:
            rep.ok("uplugin.engine_version", cat, "EngineVersion %s" % ev, tr("4.3.6.a"))
        fab = data.get("FabURL")
        if fab:
            good = re.match(r"^com\.epicgames\.launcher://ue/Fab/product/[0-9a-fA-F-]{8,}$", str(fab))
            rep.check("uplugin.fab_url", cat, not good, "FabURL is well formed",
                      'FabURL "%s" should be com.epicgames.launcher://ue/Fab/product/<listing id>' % fab, tr("4.3.6.c"))
        else:
            rep.ask("uplugin.fab_url", cat, 'No "FabURL" yet. It can only be filled once the Fab listing exists and has an ID; '
                    "add it before the final upload", tr("4.3.6.c"), severity="blocker")
        for k, sev in (("Description", "recommended"), ("CreatedBy", "recommended"), ("DocsURL", "review risk"),
                       ("SupportURL", "review risk"), ("VersionName", "recommended"), ("FriendlyName", "recommended")):
            if not str(data.get(k, "")).strip():
                rep.ask("uplugin." + k.lower(), cat, 'Empty or missing "%s"' % k,
                        tr("4.3.8.a") if k == "DocsURL" else (tr("1.1.b") if k == "SupportURL" else TROUBLE), severity=sev)
        mods = data.get("Modules") or []
        rep.facts["modules"] = [{"Name": m.get("Name"), "Type": m.get("Type")} for m in mods if isinstance(m, dict)]
        rep.check("uplugin.has_module", cat, not mods, "%d code module(s) declared" % len(mods),
                  "No code modules; a code plugin needs at least one C++ module", tr("4.3.6.1.c"))
        bad_type, no_plat, bad_phase, missing_dir, bad_plat = [], [], [], [], []
        plats = set()
        for m in mods:
            if not isinstance(m, dict):
                continue
            n = m.get("Name", "?")
            if m.get("Type") not in MODULE_TYPES:
                bad_type.append("%s:%s" % (n, m.get("Type")))
            if m.get("LoadingPhase") and m["LoadingPhase"] not in LOADING_PHASES:
                bad_phase.append("%s:%s" % (n, m["LoadingPhase"]))
            keys = [k for k in ("PlatformAllowList", "PlatformDenyList", "WhitelistPlatforms", "BlacklistPlatforms") if k in m]
            if not keys:
                no_plat.append(n)
            for k in keys:
                plats.update(m[k])
                bad_plat += ["%s:%s" % (n, p) for p in m[k] if p in BAD_PLATFORMS]
            if not any(f.lower() == ("source/%s/%s.build.cs" % (n, n)).lower() for f in files):
                missing_dir.append(n)
        rep.facts["platforms"] = sorted(plats)
        rep.check("uplugin.module_types", cat, bad_type, "Module types are valid", "Unknown module Type values", TROUBLE, sample=bad_type)
        rep.check("uplugin.loading_phase", cat, bad_phase, "Loading phases are valid", "Unknown LoadingPhase values", TROUBLE, sample=bad_phase)
        rep.check("uplugin.platform_lists", cat, no_plat, "Every module has PlatformAllowList/PlatformDenyList",
                  "Modules without PlatformAllowList or PlatformDenyList (UE4: WhitelistPlatforms/BlacklistPlatforms)", tr("4.3.6.b"), sample=no_plat)
        rep.check("uplugin.platform_names", cat, bad_plat, "No retired platform names", "Retired platform names (HTML5 breaks the build)", TROUBLE, sample=bad_plat)
        rep.check("uplugin.module_sources", cat, missing_dir, "Every module has Source/<Module>/<Module>.Build.cs",
                  "Declared modules with no Source/<Module>/<Module>.Build.cs (build error: could not find definition for module)", TROUBLE, sample=missing_dir)
        deps = [p.get("Name") for p in data.get("Plugins", []) if isinstance(p, dict) and p.get("Enabled", True)]
        if deps:
            rep.facts["plugin_dependencies"] = deps
            rep.ask("uplugin.dependencies", cat, "Depends on plugins %s; each must ship with the engine (no user-made plugins), "
                    "and experimental/beta ones must be stated in the description" % deps, tr("4.3.6.d") + "; " + tr("4.3.1.d"))
        has_content = any(f.lower().startswith("content/") for f in files)
        if has_content and not data.get("CanContainContent"):
            rep.fail("uplugin.can_contain_content", cat, 'Content/ exists but "CanContainContent" is not true, so its assets will not load', TROUBLE)
    # structure
    scat = "Structure and naming"
    check_leftovers(tree, rep, root, LOCAL_DIRS, tr("4.3.7.3.a"))
    rep.check("plugin.source", scat, not any(f.lower().startswith("source/") for f in files),
              "Source/ folder present", "No Source/ folder; Fab builds plugins from source", tr("4.3.6.1.a"))
    nested_proj = [f for f in files if f.endswith(".uproject")]
    rep.check("plugin.no_project", scat, nested_proj, "No .uproject inside the plugin",
              "A .uproject is inside the plugin; ship example projects separately via a link", tr("4.3.6.3.c"), sample=nested_proj)
    tops = sorted({f.split("/")[0] for f in files if "/" in f})
    extra = [t for t in tops if t.lower() not in PLUGIN_TOP_OK and t.lower() not in LOCAL_DIRS]
    filt = next((f for f in files if f.lower() == "config/filterplugin.ini"), None)
    ftxt = tree.text(join(root, filt)) if filt else ""
    unlisted = [t for t in extra if ("/%s/" % t).lower() not in ftxt.lower()]
    rep.check("plugin.filterplugin", scat, unlisted, "Extra top-level folders are listed in Config/FilterPlugin.ini" if extra else "No extra top-level folders",
              "Top-level folders not listed in Config/FilterPlugin.ini (they are stripped from the build)", tr("4.3.7.3.b"), sample=unlisted)
    check_names_paths(tree, rep, root, "Content/", 170, tr("4.3.7.1"), tr("4.3.7.3.c"), top, check_len=False)
    long_any = [top + "/" + f for f in files if len(top + "/" + f) > 170]
    rep.check("paths.length", scat, long_any, "All paths are 170 characters or less (measured from the plugin folder)",
              "Paths longer than 170 characters", tr("4.3.7.3.c"), sample=long_any)
    if up and (top != os.path.splitext(up)[0] or not UE_NAME_OK.match(top)):
        rep.ask("plugin.folder_name", scat, 'Plugin folder "%s" should match the descriptor name "%s" (letters, digits, underscores); '
                "zip the folder under that name" % (top, os.path.splitext(up)[0]), tr("4.3.7.3.a") + "; " + TROUBLE, severity="review risk")
    # code
    ccat = "C++ code"
    srcs = [f for f in files if ext_of(f) in (".h", ".hpp", ".cpp", ".c", ".cc", ".inl") and f.lower().startswith("source/")
            and "/thirdparty/" not in ("/" + f.lower())]
    no_cr, epic_cr, years = [], [], set()
    for f in srcs:
        head = "\n".join(tree.text(join(root, f)).splitlines()[:8])
        if "Fill out your copyright notice" in head or "Copyright Epic Games" in head:
            epic_cr.append(f)
        m = re.search(r"(//|/\*|\*).*(Copyright|\(c\)|\u00a9).*?((19|20)\d\d)", head, re.I)
        if not m:
            no_cr.append(f)
        else:
            years.add(int(m.group(3)))
    rep.check("code.copyright", ccat, no_cr, "All %d source/header files carry a copyright comment with a year" % len(srcs),
              "Source/header files without a copyright comment naming you and a year", tr("4.3.6.1.b"), sample=no_cr)
    rep.check("code.copyright_not_epic", ccat, epic_cr, "No default Epic/template copyright lines",
              "Files still carry the auto-generated Epic/template notice", tr("4.3.6.1.b"), sample=epic_cr)
    if years and max(years) < date.today().year:
        rep.ask("code.copyright_year", ccat, "Copyright years %s; Fab asks for the year you intend to publish" % sorted(years),
                tr("4.3.6.1.b"), severity="recommended")
    builds = [f for f in files if f.lower().endswith(".build.cs")]
    no_pch, abs_inc, rel_inc = [], [], []
    for f in builds:
        t = tree.text(join(root, f))
        if "UseExplicitOrSharedPCHs" not in t:
            no_pch.append(f)
        if re.search(r'"[A-Za-z]:[\\/]', t):
            abs_inc.append(f)
        for m in re.finditer(r'(Public|Private)IncludePaths\.Add(Range)?\(([^;]*)\)', t):
            if '"' in m.group(3) and "ModuleDirectory" not in m.group(3) and "PluginDirectory" not in m.group(3):
                rel_inc.append(f)
    if no_pch:
        rep.ask("code.iwyu", ccat, "Build.cs without PCHUsage = UseExplicitOrSharedPCHs: " + ", ".join(no_pch), tr("4.3.6.2.c"), severity="recommended")
    else:
        rep.ok("code.iwyu", ccat, "Build.cs files use explicit/shared PCHs (IWYU)", tr("4.3.6.2.c"))
    rep.check("code.build_abs_paths", ccat, abs_inc, "No absolute paths in Build.cs", "Absolute paths in Build.cs", tr("4.3.6.2.e"), sample=abs_inc)
    rep.check("code.include_paths", ccat, sorted(set(rel_inc)), "Include paths are built from ModuleDirectory",
              "Include paths given as bare strings; build them with Path.Combine(ModuleDirectory, ...)", tr("4.3.6.2.e"), severity="review risk", sample=sorted(set(rel_inc)))
    libs = [f for f in files if ext_of(f) in BINARY_LIB_EXT and not f.lower().startswith("source/thirdparty/")]
    rep.check("code.no_prebuilt_outside_thirdparty", ccat, libs, "No prebuilt libraries outside Source/ThirdParty",
              "Prebuilt binaries outside Source/ThirdParty (closed-source UE code is not allowed; third-party libs go in Source/ThirdParty)",
              tr("4.3.6.1.a") + "; " + tr("4.3.7.3.d"), sample=libs)
    # third party
    lcat = "Legal and third-party"
    tp = sorted({"/".join(f.split("/")[:3]) for f in files if f.lower().startswith("source/thirdparty/") and f.count("/") >= 3})
    unlicensed = [d for d in tp if not any(LICENSE_FILE.search(os.path.basename(f)) for f in files if f.startswith(d + "/"))]
    if tp:
        rep.facts["third_party_dirs"] = tp
        rep.check("legal.thirdparty_licenses", lcat, unlicensed, "Every Source/ThirdParty library has a licence file",
                  "ThirdParty libraries without a licence file", tr("4.3.7.3.d") + "; " + tr("4.2.5.b"), sample=unlicensed)
        rep.ask("legal.thirdparty_form", lcat, "Third-party code found: declare it on the listing and fill Epic's third-party software form",
                tr("4.2.5"), severity="blocker")
    check_python(tree, rep, root)
    check_docs(tree, rep, root, tr("4.3.8"))
    check_text_hygiene(tree, rep, root)
    check_images(tree, rep, root, 16384, tr("4.3.3.1"))


def check_python(tree, rep, root, forbid_all=False):
    py = [f for f in tree.under(root) if f.endswith(".py")]
    if not py:
        return
    if forbid_all:
        rep.fail("python.forbidden", "Structure and naming", "Python files are not allowed in UEFN Source: " + ", ".join(py[:5]), UEFN_DOC)
        return
    bad = [f for f in py if not f.startswith("Content/Python/")]
    rep.check("python.location", "Structure and naming", bad, "Python scripts live under Content/Python",
              "Python files outside Content/Python (third-party ones go in Content/Python/Lib/site-packages)", AFF + " (Python Scripts)", sample=bad)


def check_docs(tree, rep, root, src, required=False):
    files = tree.under(root)
    docs = [f for f in files if ext_of(f) in DOC_EXT and DOC_FILE.search(f)]
    rep.facts["docs_files"] = docs[:10]
    if docs:
        rep.ok("docs.present", "Documentation", "Documentation found: " + ", ".join(docs[:3]), src)
    elif required:
        rep.fail("docs.present", "Documentation", "No documentation file (README/Documentation .md/.txt/.pdf/.html/.rtf)", src)
    else:
        rep.ask("docs.present", "Documentation", "No documentation file in the package; a linked web page or video also counts. Ask for the docs URL",
                src, severity="review risk")


# ---------------------------------------------------------------- Unreal: project / UEFN / MetaHuman
def redirectors(tree, root):
    hits = []
    for f, size in tree.under(root).items():
        if f.endswith(".uasset") and size < 16384 and b"ObjectRedirector" in tree.read(join(root, f), 16384):
            hits.append(f)
    return hits


def check_ue_project(tree, rep, root, uefn=False):
    cat = "Project descriptor" if not uefn else "UEFN project"
    files = tree.under(root)
    top = os.path.basename(root) or os.path.splitext(os.path.basename(tree.path))[0]
    ext = ".uefnproject" if uefn else ".uproject"
    desc = next((f for f in files if "/" not in f and f.endswith(ext)), None)
    proj = os.path.splitext(desc)[0] if desc else top
    rep.facts["project"] = desc
    data = None
    try:
        data = json.loads(tree.text(join(root, desc)))
        rep.ok("project.json", cat, "%s is valid JSON" % desc, TROUBLE)
    except ValueError as e:
        rep.fail("project.json", cat, "%s is not valid JSON (%s)" % (desc, e), TROUBLE)
    if not uefn and isinstance(data, dict):
        rep.facts["EngineAssociation"] = data.get("EngineAssociation")
        has_code = bool(data.get("Modules")) or any(f.lower().startswith("source/") for f in files)
        rep.check("project.no_cpp", cat, has_code, "Content-only project (no C++ modules or Source/)",
                  "Project has C++ (Modules or Source/); content products must not contain C++, ship code as a code plugin", AFF + " (Content Product)")
        enabled = [p.get("Name") for p in data.get("Plugins", []) if isinstance(p, dict) and p.get("Enabled")]
        if enabled:
            rep.facts["enabled_plugins"] = enabled
            rep.ask("project.plugins", cat, "Plugins enabled in the .uproject: %s. Unused ones must be set Enabled=false; required ones must be "
                    "available on Fab and named in the description" % enabled, tr("4.3.1.e") + "; " + tr("4.3.1.f"))
    scat = "Structure and naming"
    check_leftovers(tree, rep, root, LOCAL_DIRS | {"plugins", "source"} if not uefn else LOCAL_DIRS,
                    tr("4.3.7.2.a") if not uefn else UEFN_DOC + " (Step 3)")
    if not uefn:
        rep.check("project.config", scat, not any(f.lower().startswith("config/") for f in files), "Config/ present",
                  "Config/ folder missing (expected: Config, Content, <Project>.uproject)", tr("4.3.7.2.a"), severity="review risk")
    content = [f for f in files if f.startswith("Content/")]
    rep.check("project.content", scat, not content, "Content/ has %d files" % len(content), "No Content/ folder", AFF)
    tops = sorted({f.split("/")[1] if f.count("/") > 1 else "(file) " + f.split("/")[1] for f in content})
    if not uefn:
        rep.check("project.single_root", scat, len(tops) != 1, "All assets are inside one folder under Content/: %s" % (tops[0] if tops else ""),
                  "Content/ must contain exactly one top-level folder and no loose files; found %s" % tops, tr("4.3.7.2.b"))
        if len(tops) == 1 and tops[0] != proj:
            rep.ask("project.root_name", scat, 'Content folder "%s" differs from project name "%s"; Fab\'s structure guide expects the pack '
                    "folder to be named after the product" % (tops[0], proj), AFF + " (Unreal Engine Project Technical Requirements)", severity="recommended")
    pack = "Content/" + tops[0] + "/" if len(tops) == 1 and not uefn else "Content/"
    check_names_paths(tree, rep, root, pack, 140, tr("4.3.7.1") if not uefn else tr("6.3.6.1"),
                      tr("4.3.7.2.d") if not uefn else tr("6.3.6.2.c"), tops[0] if (len(tops) == 1 and not uefn) else top)
    loose_in_pack = [f for f in files if f.startswith(pack) and f.count("/") == pack.count("/") and f.endswith(".uasset")]
    if loose_in_pack and not uefn:
        rep.ask("project.sorted_folders", scat, "%d assets sit loose in the pack root; sort them into folders by type or set" % len(loose_in_pack),
                tr("4.3.7.2.c"), severity="review risk")
    ccat = "Content"
    maps = [f for f in files if f.endswith(".umap")]
    rep.facts["maps"] = maps[:20]
    rep.facts["uasset_count"] = sum(1 for f in files if f.endswith(".uasset"))
    if maps:
        rep.ok("content.maps", ccat, "%d map(s): %s" % (len(maps), ", ".join(os.path.basename(m) for m in maps[:4])), tr("4.3.2.a"))
    else:
        rep.fail("content.maps", ccat, "No maps. Visual products need an overview map (and some categories a demo map)",
                 tr("4.3.2.a") + "; " + AFF + " (Maps)", severity="review risk")
    red = redirectors(tree, root)
    rep.check("content.redirectors", ccat, red, "No redirector assets found",
              "Redirector assets found (Fix Up Redirectors in the editor)", tr("4.3.1.h"), sample=red)
    dev = [f for f in tops if f.lower() in ("developers", "collections")]
    if dev:
        rep.fail("content.dev_folders", ccat, "Local editor folders under Content: %s" % dev, tr("4.3.7.2.a"))
    check_python(tree, rep, root, forbid_all=uefn)
    check_docs(tree, rep, root, tr("4.3.8") if not uefn else tr("6.3.7"))
    check_text_hygiene(tree, rep, root)
    check_images(tree, rep, root, 8192 if uefn else 16384, tr("6.3.3.1.c") if uefn else tr("4.3.3.1"))


def check_metahuman(tree, rep, root):
    files = tree.under(root)
    pk = [f for f in files if f.endswith(".mhpkg")]
    rep.check("metahuman.single", "MetaHuman", len(pk) != 1, "Exactly one .mhpkg", "Expected exactly one .mhpkg, found %d" % len(pk), tr("5.2.1.b"))
    big = [f for f in pk if files[f] > 1.5 * GB]
    rep.check("metahuman.size", "MetaHuman", big, ".mhpkg is 1.5 GB or less", ".mhpkg over 1.5 GB", AFF + " (MetaHuman)", severity="review risk", sample=big)


# ---------------------------------------------------------------- Unity
def check_unity(tree, rep, root, kind):
    cat = "Unity structure"
    files = tree.under(root)
    if kind in ("unity-project", "unity-assets"):
        assets = {f[len("Assets/"):]: s for f, s in files.items() if f.startswith("Assets/")}
        check_leftovers(tree, rep, root, UNITY_LOCAL_DIRS, uas("2.1.c"))
        pv = files.get("ProjectSettings/ProjectVersion.txt")
        if pv is not None:
            m = re.search(r"m_EditorVersion:\s*(\S+)", tree.text(join(root, "ProjectSettings/ProjectVersion.txt")))
            if m:
                rep.facts["unity_editor_version"] = m.group(1)
                unity_version_check(rep, m.group(1))
    elif kind == "unity-package":
        assets = {f[len("Assets/"):]: s for f, s in files.items() if f.startswith("Assets/") and not f.endswith("/")}
        outside = [f for f in files if not f.startswith("Assets/") and not f.startswith("Packages/")]
        rep.check("unity.paths_in_assets", cat, outside, "All package paths are under Assets/", "Paths outside Assets/", uas("2.1.a"), sample=outside)
    else:
        assets = {}
    rel_assets = {k: v for k, v in assets.items() if not k.endswith(".meta")}
    rep.facts["unity_asset_count"] = len(rel_assets)
    tops = sorted({k.split("/")[0] for k in rel_assets if "/" in k} | {"(file) " + k for k in rel_assets if "/" not in k})
    roots = [t for t in tops if t.lower() not in UNITY_SPECIAL_ROOT]
    if kind == "unity-project":
        rep.ask("unity.root", cat, "Folders under Assets/: %s. Only the product folder (plus Unity special folders) goes into the .unitypackage"
                % tops, uas("2.1.a"), severity="blocker") if len(roots) != 1 else rep.ok("unity.root", cat, "One root folder under Assets/: %s" % roots[0], uas("2.1.a"))
    else:
        rep.check("unity.root", cat, len(roots) != 1, "One root folder under Assets/: %s" % (roots[0] if roots else ""),
                  "Content must sit under one root folder in Assets/ (special folders excepted); found %s" % tops, uas("2.1.a"))
    ast = [k for k in rel_assets if "assetstoretools" in k.lower()]
    rep.check("unity.assetstoretools", cat, ast, "Nothing inside an AssetStoreTools folder", "Content inside AssetStoreTools (stripped on upload)", uas("2.1.d"), sample=ast)
    long_ = ["Assets/" + k for k in rel_assets if len("Assets/" + k) >= 150]
    rep.check("unity.path_length", cat, long_, "All paths are under 150 characters from Assets/", "Paths of 150+ characters", uas("2.1.e"), sample=long_)
    vague = sorted({p for k in rel_assets for p in k.split("/")[:-1] if VAGUE_NAME.match(p)})
    rep.check("naming.vague", cat, vague, "No vaguely named folders", "Vague folder names", uas("2.1.b"), severity="review risk", sample=vague)
    if kind in ("unity-project", "unity-assets"):
        missing_meta = [k for k in rel_assets if k + ".meta" not in assets]
        rep.check("unity.meta_files", cat, missing_meta, "Every asset has a .meta file", "Assets without .meta files", uas("5.2.d"),
                  severity="review risk", sample=missing_meta)
    unity_content_checks(tree, rep, root, "Assets/" if kind != "unity-upm" else "", rel_assets if kind != "unity-upm" else
                         {k: v for k, v in files.items() if not k.endswith(".meta")})


def unity_version_check(rep, v):
    m = re.match(r"^(\d+)(?:\.(\d+))?", v)
    if not m:
        return
    major, minor = int(m.group(1)), int(m.group(2) or 0)
    old = major < 2022 or (major == 2022 and minor < 3)
    rep.check("unity.version", "Unity structure", old, "Unity version %s is 2022.3 or newer" % v,
              "Unity %s is older than 2022.3, the minimum for new submissions" % v, uas("1.3.a"))


def unity_content_checks(tree, rep, root, prefix, rel_assets):
    cat = "Unity content"
    full = lambda k: join(root, prefix + k)
    scenes = [k for k in rel_assets if k.endswith(".unity")]
    rep.facts["unity_scenes"] = scenes[:10]
    if scenes:
        rep.ok("unity.demo_scene", cat, "%d scene(s): %s" % (len(scenes), ", ".join(os.path.basename(s) for s in scenes[:3])), uas("1.1.f"))
    else:
        rep.ask("unity.demo_scene", cat, "No .unity scene; 3D, 2D, VFX, Animation and Template products need a demo scene", uas("1.1.f"))
    scripts = [k for k in rel_assets if k.endswith(".cs")]
    no_ns, unity_ns = [], []
    for k in scripts:
        t = tree.text(full(k))
        m = re.search(r"^\s*namespace\s+([A-Za-z_][\w.]*)", t, re.M)
        if not m:
            if re.search(r"\b(class|struct|interface|enum)\s+\w+", t):
                no_ns.append(k)
        elif re.match(r"^(Unity|UnityEngine|UnityEditor)(\.|$)", m.group(1)):
            unity_ns.append(k)
    if scripts:
        rep.facts["unity_script_count"] = len(scripts)
        rep.check("unity.namespaces", cat, no_ns, "All scripts declare a namespace", "Scripts without a namespace", uas("2.5.a"), sample=no_ns)
        rep.check("unity.namespace_trademark", cat, unity_ns, "No scripts in Unity-owned namespaces",
                  "Scripts in Unity/UnityEngine/UnityEditor namespaces", uas("2.5.a"), sample=unity_ns)
    docs = [k for k in rel_assets if ext_of(k) in DOC_EXT and DOC_FILE.search(k)]
    needs_docs = bool(scripts) or any(ext_of(k) in (".shader", ".shadergraph", ".compute", ".hlsl") for k in rel_assets)
    rep.facts["docs_files"] = docs[:10]
    if docs:
        rep.ok("docs.present", "Documentation", "Documentation found: " + ", ".join(docs[:3]), uas("2.3"))
    elif needs_docs:
        rep.fail("docs.present", "Documentation", "Package has code or shaders but no documentation file (.txt/.md/.pdf/.html/.rtf)", uas("2.3.a"))
    else:
        rep.ask("docs.present", "Documentation", "No documentation file; needed if the product has settings or setup steps", uas("2.3.a"), severity="recommended")
    tpn = [k for k in rel_assets if re.search(r"third[ _-]?party[ _-]?notices?", k, re.I)]
    if tpn:
        rep.ok("legal.third_party_notices", "Legal and third-party", "Third-party notices file: " + tpn[0], uas("1.2.a"))
    else:
        rep.ask("legal.third_party_notices", "Legal and third-party", "No 'Third-Party Notices.txt'; required if any fonts, audio, code or other "
                "third-party components are included", uas("1.2.a"))
    meshes = [k for k in rel_assets if ext_of(k) in DCC_EXT and ext_of(k) not in UNITY_MESH_OK]
    rep.check("unity.mesh_formats", cat, meshes, "Meshes use .fbx/.dae/.abc/.obj",
              "Source-format meshes inside Assets (.blend/.max/.ma/...); export to FBX, or zip them with 'source' in the name", uas("2.4.a"), severity="review risk", sample=meshes)
    zips = [k for k in rel_assets if ext_of(k) == ".zip" and "source" not in os.path.basename(k).lower()]
    rep.check("unity.zip_naming", cat, zips, "Any .zip holds non-Unity source files and says 'source' in its name",
              ".zip files must only carry non-Unity source files and include 'source' in the name", uas("2.2.b"), severity="review risk", sample=zips)
    nested = [k for k in rel_assets if ext_of(k) in (".unitypackage", ".unitypackage.gz")]
    if nested:
        rep.ask("unity.nested_packages", cat, "Nested .unitypackage files %s; allowed only for settings, pipeline variants or add-ons" % nested[:3], uas("2.2.a"))
    lossy_img = [k for k in rel_assets if ext_of(k) in (".jpg", ".jpeg")]
    if lossy_img:
        rep.ask("unity.lossless_images", cat, "%d JPEG images; art products should use lossless formats (.png/.tga/.psd)" % len(lossy_img), uas("2.4.3.a"), severity="recommended")
    for k in rel_assets:
        if k.endswith(".asmdef"):
            try:
                json.loads(tree.text(full(k)))
            except ValueError:
                rep.fail("unity.asmdef_json", cat, "Invalid JSON in " + k, uas("5.2.b"))
    sub = join(root, prefix.rstrip("/")) if prefix else root
    check_text_hygiene(tree, rep, sub)
    check_images(tree, rep, sub, 16384, uas("2.4.3.h"))
    check_audio(tree, rep, sub, unity=True)


def check_upm(tree, rep, root):
    cat = "Unity package manifest (package.json)"
    files = tree.under(root)
    try:
        pj = json.loads(tree.text(join(root, "package.json")))
        rep.ok("upm.json", cat, "package.json is valid JSON", uas("5.2"))
    except ValueError as e:
        rep.fail("upm.json", cat, "package.json is not valid JSON (%s)" % e, uas("5.2"))
        pj = {}
    for k in ("name", "displayName", "version", "unity", "unityRelease", "description", "author", "documentationUrl", "license"):
        if k in pj:
            rep.facts["package." + k] = pj[k]
    missing = [k for k in ("name", "displayName", "version", "unity", "unityRelease", "author", "description") if not pj.get(k)]
    rep.check("upm.required_fields", cat, missing, "Required manifest fields present", "Missing manifest fields", uas("5.2.e"), sample=missing)
    if pj.get("name"):
        rep.check("upm.name", cat, not re.match(r"^[a-z0-9-_]+(\.[a-z0-9-_]+){2,}$", pj["name"]) or pj["name"].startswith("com.unity."),
                  "Package name is reverse-domain lowercase", 'Name "%s" should be reverse-domain lowercase (com.company.package) and not com.unity.*' % pj["name"], uas("5.2.f"))
    if pj.get("version"):
        rep.check("upm.semver", cat, not re.match(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$", pj["version"]),
                  "Version is valid semver", 'Version "%s" is not semver' % pj["version"], uas("5.2.g"))
    if pj.get("unity"):
        unity_version_check(rep, pj["unity"])
    deps = pj.get("dependencies") or {}
    nonunity = [d for d in deps if not d.startswith("com.unity.")]
    if nonunity:
        rep.ask("upm.dependencies", cat, "Non-Unity dependencies %s must be part of the same product" % nonunity, uas("5.2.c"))
    for k, sev in (("documentationUrl", "review risk"), ("license", "recommended")):
        if not pj.get(k):
            rep.ask("upm." + k.lower(), cat, 'Empty "%s"' % k, uas("2.3.a") if k == "documentationUrl" else UAS, severity=sev)
    for name, rx, sev in (("CHANGELOG.md", r"^changelog\.md$", "recommended"), ("Documentation~", r"^documentation~/", "recommended"),
                          ("LICENSE.md", r"^licen[cs]e(\.md)?$", "recommended")):
        has = any(re.match(rx, f, re.I) for f in files)
        if has:
            rep.ok("upm." + name.lower(), cat, name + " present", uas("2.3"))
        else:
            rep.ask("upm." + name.lower(), cat, name + " missing", uas("2.3"), severity=sev)
    missing_meta = [f for f in files if not f.endswith(".meta") and f != "package.json.meta" and "~/" not in f and not f.startswith(".")
                    and f + ".meta" not in files and not f.endswith("~")]
    rep.check("unity.meta_files", "Unity structure", missing_meta, "Every package file has a .meta file", "Files without .meta", uas("5.2.d"),
              severity="review risk", sample=missing_meta)
    top = pj.get("name") or os.path.basename(root)
    long_ = [top + "/" + f for f in files if len(top + "/" + f) >= 150]
    rep.check("unity.path_length", "Unity structure", long_, "All paths under 150 characters", "Paths of 150+ characters", uas("2.1.e"), sample=long_)
    unity_content_checks(tree, rep, root, "", {k: v for k, v in files.items() if not k.endswith(".meta")})


# ---------------------------------------------------------------- DCC / loose files
def check_dcc(tree, rep, root):
    cat = "3D exchange and DCC files"
    files = tree.under(root)
    exts = sorted({ext_of(f) for f in files if ext_of(f) in DCC_EXT})
    rep.facts["3d_formats"] = exts
    fams = {e if e not in (".usda", ".usdc") else ".usd" for e in exts}
    if len(fams) > 1:
        rep.ask("dcc.one_format", cat, "Several 3D formats %s; each Fab format upload must contain only that format (upload one per format)" % exts,
                tr("2.1"))
    else:
        rep.ok("dcc.one_format", cat, "Single 3D format %s" % exts, tr("2.1"))
    bad_refs = []
    for f in files:
        e = ext_of(f)
        if e == ".gltf":
            try:
                g = json.loads(tree.text(join(root, f)))
            except ValueError:
                rep.fail("dcc.gltf_json", cat, "Invalid glTF JSON: " + f, tr("2.3.2.1.a"))
                continue
            for item in g.get("buffers", []) + g.get("images", []):
                uri = item.get("uri", "")
                if uri and not uri.startswith("data:"):
                    p = os.path.normpath(os.path.join(os.path.dirname(f), uri)).replace(os.sep, "/")
                    if os.path.isabs(uri) or re.match(r"^[A-Za-z]:", uri) or p not in files:
                        bad_refs.append("%s -> %s" % (f, uri))
        elif e in (".obj", ".mtl"):
            for line in tree.text(join(root, f)).splitlines():
                parts = line.strip().split(None, 1)
                if len(parts) == 2 and (parts[0] == "mtllib" or parts[0].startswith("map_") or parts[0] in ("bump", "disp", "norm")):
                    ref = parts[1].split()[-1]
                    p = os.path.normpath(os.path.join(os.path.dirname(f), ref)).replace(os.sep, "/")
                    if re.match(r"^([A-Za-z]:|/)", ref) or p not in files:
                        bad_refs.append("%s -> %s" % (f, ref))
    rep.check("dcc.references", cat, bad_refs, "Material/texture references resolve inside the package",
              "Broken or absolute texture/material references", tr("2.3.2.1.a"), sample=bad_refs)
    check_text_hygiene(tree, rep, root)
    check_images(tree, rep, root, 16384, tr("4.3.3.1"))


# ---------------------------------------------------------------- main
def audit(path):
    path = os.path.abspath(path)
    rep = Report(path)
    tree = Tree(path)
    types = detect(tree)
    rep.detected = types
    if not types:
        rep.ask("detect.unknown", "Detection", "No Unreal, UEFN, Unity, MetaHuman or 3D/audio files recognised; ask the user what the product is", PUB)
    check_package(tree, rep, types)
    tset = [t["type"] for t in types]
    plugin_roots = [t["root"] for t in types if t["type"] == "ue-plugin"]
    for t in types:
        r = t["root"]
        if t["type"] == "ue-plugin":
            check_ue_plugin(tree, rep, r)
        elif t["type"] == "ue-project":
            if plugin_roots and any(p.startswith(join(r, "Plugins/")) for p in plugin_roots):
                rep.ask("detect.plugin_in_project", "Detection", "A plugin sits inside a host project (%s). For a code-plugin listing, "
                        "audit and zip the plugin folder alone; the project can become a linked example project" % r, tr("4.3.6.3"), severity="blocker")
            check_ue_project(tree, rep, r)
        elif t["type"] == "uefn":
            check_ue_project(tree, rep, r, uefn=True)
        elif t["type"] == "metahuman":
            check_metahuman(tree, rep, r)
        elif t["type"] in ("unity-project", "unity-assets", "unity-package"):
            check_unity(tree, rep, r, t["type"])
        elif t["type"] == "unity-upm":
            check_upm(tree, rep, r)
        elif t["type"] == "unity-package-file":
            sub = audit(os.path.join(path, r)) if tree.kind == "dir" else None
            if sub:
                for x in sub.results:
                    x["id"] = os.path.basename(r) + ":" + x["id"]
                rep.results += sub.results
                rep.facts.update({os.path.basename(r) + ":" + k: v for k, v in sub.facts.items()})
        elif t["type"] == "dcc-3d":
            check_dcc(tree, rep, r)
        elif t["type"] == "audio-files":
            check_audio(tree, rep, r)
    if len({x for x in tset if x.startswith("ue")} | {x for x in tset if x.startswith("unity")}) > 1 and "detect.plugin_in_project" not in [x["id"] for x in rep.results]:
        rep.ask("detect.multiple", "Detection", "Several product types found %s; confirm which one is being published" % tset, PUB, severity="blocker")
    return rep


# ---------------------------------------------------------------- self-test
def _write(base, rel, text):
    p = os.path.join(base, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    mode = "wb" if isinstance(text, bytes) else "w"
    with open(p, mode, **({} if mode == "wb" else {"encoding": "utf-8", "newline": "\n"})) as f:
        f.write(text)


def make_fixtures(base):
    """Create bad_plugin/, clean_plugin/ and bad_unity/ under base. Returns their paths."""
    year = date.today().year
    clean = os.path.join(base, "clean_plugin", "CleanTool")
    up = {"FileVersion": 3, "Version": 1, "VersionName": "1.0.0", "FriendlyName": "Clean Tool", "Description": "Adds a clean tool.",
          "Category": "Editor", "CreatedBy": "Example Studio", "CreatedByURL": "https://example.com", "DocsURL": "https://example.com/docs",
          "SupportURL": "https://example.com/support", "EngineVersion": "5.6.0",
          "FabURL": "com.epicgames.launcher://ue/Fab/product/ad53b85f109c87b4a8bf580898186114", "CanContainContent": True,
          "Modules": [{"Name": "CleanTool", "Type": "Editor", "LoadingPhase": "Default", "PlatformAllowList": ["Win64", "Mac", "Linux"]}]}
    _write(clean, "CleanTool.uplugin", json.dumps(up, indent=1))
    hdr = "// Copyright %d Example Studio. All rights reserved.\n" % year
    _write(clean, "Source/CleanTool/CleanTool.Build.cs", hdr + "using System.IO;\nusing UnrealBuildTool;\npublic class CleanTool : ModuleRules {\n"
           " public CleanTool(ReadOnlyTargetRules T) : base(T) {\n  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;\n"
           '  PublicIncludePaths.Add(Path.Combine(ModuleDirectory, "Public"));\n  PublicDependencyModuleNames.Add("Core");\n }\n}\n')
    _write(clean, "Source/CleanTool/Public/CleanTool.h", hdr + "#pragma once\n#include \"Modules/ModuleManager.h\"\n")
    _write(clean, "Source/CleanTool/Private/CleanTool.cpp", hdr + "#include \"CleanTool.h\"\nIMPLEMENT_MODULE(FDefaultModuleImpl, CleanTool)\n")
    _write(clean, "Source/ThirdParty/TinyLib/LICENSE.txt", "MIT License\n")
    _write(clean, "Source/ThirdParty/TinyLib/tiny.h", "// TinyLib (MIT)\n")
    _write(clean, "Content/Icons/T_CleanTool_Icon.uasset", b"\x00" * 4096)
    _write(clean, "Resources/Icon128.png", b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 128, 128) + b"\x08\x06\x00\x00\x00")
    _write(clean, "Docs/README.md", "# Clean Tool\nUsage...\n")
    _write(clean, "Config/FilterPlugin.ini", "[FilterPlugin]\n/Docs/...\n")

    bad = os.path.join(base, "bad_plugin", "Bad Tool")
    up_bad = '{ "FileVersion": 3, "FriendlyName": "Bad", "Modules": [ { "Name": "BadTool", "Type": "Runtimee" }, ' \
             '{ "Name": "Missing", "Type": "Runtime", "PlatformAllowList": ["Win64", "HTML5"] } ], }'  # trailing comma = invalid JSON
    _write(bad, "BadTool.uplugin", up_bad)
    _write(bad, "Source/BadTool/BadTool.Build.cs", 'public class BadTool : ModuleRules { public BadTool(ReadOnlyTargetRules T) : base(T) {\n'
           ' PublicIncludePaths.Add("C:/Users/dev/Projects/BadTool/Source/BadTool/Public"); } }\n')
    _write(bad, "Source/BadTool/Private/BadTool.cpp", "// Copyright Epic Games, Inc. All Rights Reserved.\n#include \"BadTool.h\"\n")
    _write(bad, "Source/BadTool/Public/BadTool.h", "#pragma once\n// GNU General Public License v3\n")
    _write(bad, "Source/ThirdParty/SomeLib/some.h", "int f();\n")
    _write(bad, "Binaries/Win64/UnrealEditor-BadTool.dll", b"MZ")
    _write(bad, "Intermediate/Build/x.txt", "x")
    _write(bad, "Content/New Folder/My-Asset.uasset", b"\x00" * 64)
    _write(bad, "Content/" + "VeryLongFolderName_" * 9 + "/A.uasset", b"\x00")
    _write(bad, "Docs/Readme.txt", "see C:\\Users\\dev\\Desktop\\notes.txt\n")
    _write(bad, "Tools/setup.exe", b"MZ")
    _write(bad, "Content/Python/tool.py", "print('ok')\n")
    _write(bad, "Scripts/helper.py", "print('x')\n")

    unity = os.path.join(base, "bad_unity")
    _write(unity, "ProjectSettings/ProjectVersion.txt", "m_EditorVersion: 2021.3.10f1\n")
    _write(unity, "Assets/MyPack/Scripts/Player.cs", "using UnityEngine;\npublic class Player : MonoBehaviour {}\n")
    _write(unity, "Assets/MyPack/Scripts/Player.cs.meta", "guid: 1\n")
    _write(unity, "Assets/Other/Thing.cs", "namespace UnityEngine.Extra { public class Thing {} }\n")
    _write(unity, "Assets/MyPack/Models/rock.blend", b"BLENDER")
    _write(unity, "Assets/AssetStoreTools/x.txt", "x")

    proj = os.path.join(base, "bad_project", "MyPack")
    _write(proj, "MyPack.uproject", json.dumps({"FileVersion": 3, "EngineAssociation": "5.6", "Modules": [{"Name": "MyPack", "Type": "Runtime"}],
                                                "Plugins": [{"Name": "Water", "Enabled": True}]}))
    _write(proj, "Content/MyPack/Meshes/SM_Rock.uasset", bytes(32))
    _write(proj, "Content/MyPack/Meshes/SM_Old.uasset", bytes(2) + b"ObjectRedirector" + bytes(1))
    _write(proj, "Content/Loose.uasset", bytes(1))
    _write(proj, "Saved/Logs/x.log", "x")
    _write(proj, "Source/MyPack/MyPack.Build.cs", "// x\n")

    upm = os.path.join(base, "bad_upm", "com.example.tool")
    _write(upm, "package.json", json.dumps({"name": "com.example.tool", "displayName": "Tool", "version": "1.0", "unity": "2022.3",
                                            "description": "Example tool"}))
    _write(upm, "package.json.meta", "x")
    _write(upm, "Runtime/Tool.cs", "namespace Example.Tool { public class Tool {} }\n")
    return {"clean": clean, "bad": bad, "unity": unity, "project": proj, "upm": upm}


def selftest():
    with tempfile.TemporaryDirectory() as td:
        fx = make_fixtures(td)
        clean = audit(fx["clean"])
        fails = [r for r in clean.results if r["status"] == "fail"]
        assert not fails, "clean plugin should have no failures: %s" % fails
        assert clean.detected == [{"type": "ue-plugin", "root": ""}], clean.detected
        zpath = os.path.join(td, "CleanTool.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for dp, _, fns in os.walk(fx["clean"]):
                for fn in fns:
                    full = os.path.join(dp, fn)
                    z.write(full, os.path.join("CleanTool", os.path.relpath(full, fx["clean"])))
        zrep = audit(zpath)
        assert not [r for r in zrep.results if r["status"] == "fail"], "zipped clean plugin should pass"

        bad = audit(fx["bad"])
        failed = {r["id"] for r in bad.results if r["status"] == "fail"}
        expected = {"uplugin.json", "structure.local_folders", "files.forbidden", "code.copyright", "code.copyright_not_epic",
                    "code.build_abs_paths", "code.include_paths", "code.no_prebuilt_outside_thirdparty", "legal.thirdparty_licenses",
                    "legal.copyleft", "naming.charset", "naming.vague", "paths.length", "text.absolute_paths", "python.location"}
        missing = expected - failed
        assert not missing, "bad plugin: expected failures not reported: %s" % sorted(missing)
        # descriptor checks on a parseable but broken .uplugin
        _write(fx["bad"], "BadTool.uplugin", json.dumps({"FileVersion": 3, "EngineVersion": "5.6", "Modules": [
            {"Name": "BadTool", "Type": "Runtimee"}, {"Name": "Missing", "Type": "Runtime", "PlatformAllowList": ["Win64", "HTML5"]}]}))
        bad2 = audit(fx["bad"])
        failed2 = {r["id"] for r in bad2.results if r["status"] == "fail"}
        for i in ("uplugin.engine_version", "uplugin.module_types", "uplugin.platform_lists", "uplugin.platform_names", "uplugin.module_sources"):
            assert i in failed2, "expected %s in %s" % (i, sorted(failed2))
        asks = {r["id"] for r in bad2.results if r["status"] == "ask"}
        assert "uplugin.fab_url" in asks

        un = audit(fx["unity"])
        assert un.detected == [{"type": "unity-project", "root": ""}], un.detected
        f3 = {r["id"] for r in un.results if r["status"] == "fail"}
        for i in ("unity.version", "unity.namespaces", "unity.namespace_trademark", "unity.mesh_formats", "unity.assetstoretools",
                  "unity.meta_files", "docs.present"):
            assert i in f3, "unity: expected %s in %s" % (i, sorted(f3))
        pr = audit(fx["project"])
        f4 = {r["id"] for r in pr.results if r["status"] == "fail"}
        for i in ("project.no_cpp", "project.config", "project.single_root", "structure.local_folders", "content.redirectors", "content.maps"):
            assert i in f4, "project: expected %s in %s" % (i, sorted(f4))
        up = audit(fx["upm"])
        assert up.detected == [{"type": "unity-upm", "root": ""}], up.detected
        f5 = {r["id"] for r in up.results if r["status"] == "fail"}
        for i in ("upm.required_fields", "upm.semver", "unity.meta_files", "docs.present"):
            assert i in f5, "upm: expected %s in %s" % (i, sorted(f5))
        # read-only guarantee: fixture files unchanged
        assert os.path.exists(os.path.join(fx["bad"], "Binaries", "Win64", "UnrealEditor-BadTool.dll"))
    print("selftest OK: clean plugin (folder and zip) has 0 failures; bad plugin raised %d expected failures; "
          "descriptor checks raised 5; Unity project raised 7; UE content project raised 6; UPM package raised 4" % len(expected))
    return 0


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    if "--selftest" in argv:
        return selftest()
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    if not os.path.exists(args[0]):
        print("No such path: " + args[0])
        return 2
    rep = audit(args[0])
    if "--json" in argv:
        print(json.dumps(rep.to_json(), indent=2, ensure_ascii=False))
    else:
        print(rep.render())
    return 1 if rep.summary()["fail"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
