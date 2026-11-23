# -*- coding: utf-8 -*-
"""
COCORO - Trình Cài Đặt Patch Việt Hóa (GUI Installer)
Bản Việt Hóa Trọn Vẹn 50 Chương (Full Game)
Hỗ trợ chọn thư mục, tự động sao lưu, cài đặt patch và khôi phục bản gốc.
"""
from __future__ import annotations
import os
import sys
import shutil
import struct
import zlib
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Static filter states for scenario entries 784..833 (Full Game 50 Scenarios)
FILTER_STATES = {
    784: bytes.fromhex("a35c7fff3df37ffff1dfe00df3c36d0b3b030000000000002c00000001000000c84d00000100f2520000000001000000"),
    785: bytes.fromhex("65b3430b44e2cb6b5ed6cbff5ed6cbff7d0500000000000038000000010000006008e50002d758390000000001000000"),
    786: bytes.fromhex("c9b2ed371a95ad0d5f2a76465ec01f914103000000000000a800000001000000db9d000001004f650000000001000000"),
    787: bytes.fromhex("b1589258b1589258d43c90e3d7f73f06bd0200000000000089000000010000000da47100a4e3f2800000000001000000"),
    788: bytes.fromhex("0bd0a4cc015b30c724eee77500107f33fb020000000000007200000001000000b9cc3500b9cc35860000000001000000"),
    789: bytes.fromhex("895fc963895fc963773664ff7b8163497d03000000000000b900000001000000ba70a60043e7ae4b0000000001000000"),
    790: bytes.fromhex("79ca334679ca3346c3fb833174b7ce0b7d03000000000000fc000000010000000f4831007b6da3270000000001000000"),
    791: bytes.fromhex("23c3f4b721f77087ffe3a382ffe3a3823b030000000000001500000001000000a3513d001e4f831c0000000001000000"),
    792: bytes.fromhex("1a2bb2361a2bb236ffdb278fffff6386bf02000000000000a50000000100000020eb4c00e0cb918c0000000001000000"),
    793: bytes.fromhex("53b463c92d46f5aa88010f3275605b7b41030000000000004a000000010000009bda3d006ae435080000000001000000"),
    794: bytes.fromhex("fa7589e8f982a2ae29ed3ffa2ecf647abf02000000000000fd00000001000000b9cc3500b9cc35860000000001000000"),
    795: bytes.fromhex("c7479b37dee7dc1fd51e15e0aae1ea1fbd02000000000000c200000001000000e6627b00192d982a0000000001000000"),
    796: bytes.fromhex("0a66ee7ae99a4460a5ad26fca5ad26fcfb04000000000000a5000000010000009267a8007efd3bd90000000001000000"),
    797: bytes.fromhex("b813b20eb6912ca95fdf5beb6b76ac180105000000000000a500000001000000d76c930053f9c2640000000001000000"),
    798: bytes.fromhex("ea25b7ffea9a5c92fff02ea3fffffa2b8105000000000000a5000000010000008e3bd3005492c71b0000000001000000"),
    799: bytes.fromhex("7f209e55da3e15f88fdc6a7f0a3f71a97d03000000000000e400000001000000462800000100e9f90000000001000000"),
    800: bytes.fromhex("ad3ee24bd8249781f9aa7e17f82a8177bb04000000000000b900000001000000ba8f8a007c489a130000000001000000"),
    801: bytes.fromhex("5c93e987cc0c8d87ffe3a382ffe3a38281050000000000001400000001000000e71c0000010068190000000001000000"),
    802: bytes.fromhex("52c553da7890b429df99c89aebbc3f69ff020000000000002800000001000000a5000000010000000000000001000000"),
    803: bytes.fromhex("afac3f7776a773f4f432e117bef15ee6fb02000000000000a500000001000000aedb4c0041ea70150000000001000000"),
    804: bytes.fromhex("ffe3a382ffe3a3828ecb575ccb3fb9c43b05000000000000a56000000100390282853700803eca390000000001000000"),
    805: bytes.fromhex("d5753aaeaa8ac5518e070ba58a19ec8ac1040000000000000300000001000000878e820045ea261b0000000001000000"),
    806: bytes.fromhex("895fc963895fc963773664ff7b8163493d03000000000000b9000000010000001a98fb009c9f4c870000000001000000"),
    807: bytes.fromhex("ffffd769ffa13607ffe3a382ffe3a382bf04000000000000a5000000010000001d1a770036bdac120000000001000000"),
    808: bytes.fromhex("7b2e2487433b06d345fc8b1995a11fb43b03000000000000c900000001000000d0b700000100f2890000000001000000"),
    809: bytes.fromhex("d536db99aac92466e2a006939ba27fff810300000000000003000000010000009c71530073da20200000000001000000"),
    810: bytes.fromhex("644f2c4a417f13b0029b79f70d53f7433f03000000000000a50000000100000036cd5800c7e249200000000001000000"),
    811: bytes.fromhex("12bf76ab89b3212b6509feef0d2753aabf020000000000006e000000010000007a9db700bb55fe070000000001000000"),
    812: bytes.fromhex("66d5c69c678f81910038146d69d5e345fb0400000000000054000000010000002583250010f2cfce0000000001000000"),
    813: bytes.fromhex("ffe3a382e3a382041f078e4663064773bd02000000000000a5000000010000002a564100cbdf1ba10000000001000000"),
    814: bytes.fromhex("fef4feadffff7a7ff70b7423f30b7901c104000000000000b400000001000000a847f000b9f9f0180000000001000000"),
    815: bytes.fromhex("a54827a5860d2aceac4dd56dc9dd64323f05000000000000c000000001000000c6f1330098c1df240000000001000000"),
    816: bytes.fromhex("1512c6890c3fbde5bba429c7bba429c77f0500000000000014000000010000005cc23800a33dc72a0000000001000000"),
    817: bytes.fromhex("430b355be1f4314d35273b17318eebdc4103000000000000a500000001000000e6608000192f932b0000000001000000"),
    818: bytes.fromhex("fe8e7fdaf4a56cc605acbf8b330691b1fb04000000000000800000000100000062991d00af88541a0000000001000000"),
    819: bytes.fromhex("0c2bb4330c2bb433c1623be779dacbbfc1020000000000006000000001000000fd6de800af86fd5b0000000001000000"),
    820: bytes.fromhex("c0d3c333c4ebad766180ad1e654f745e3f03000000000000b90000000100000057000000010000000000000001000000"),
    821: bytes.fromhex("b20b3602efc2e102fb0015fda77954c03d030000000000001c00000001000000c06ac500f1b7a91d0000000001000000"),
    822: bytes.fromhex("e5cce9ffe674fffff780ce0df365520bfd040000000000009200000001000000c9d44d00d4e5c94d0000000001000000"),
    823: bytes.fromhex("469607619507a36cf7c36dff2fb63bfffb040000000000007a000000010000008d7c6e00a4d8f3b90000000001000000"),
    824: bytes.fromhex("24aa36cf1e5e6826b68beb8e92e0a1bdc1020000000000006f0000000100000043b4200020f247950000000001000000"),
    825: bytes.fromhex("1afa6a2a1ae3af6fa26fcee669af173301050000000000001200000001000000b9ff3e00ff5eb93e0000000001000000"),
    826: bytes.fromhex("12318994f1e407c9b8df87ffc5b46affbf040000000000004800000001000000b6743b004ba40d0a0000000001000000"),
    827: bytes.fromhex("728587a9e6d92ca4dcd53dfadcd53dfabb02000000000000c80000000100000094338b006b5c882a0000000001000000"),
    828: bytes.fromhex("18d560184d8aadd20262624004ceb7aefd04000000000000830000000100000013a2b800ed9dc8740000000001000000"),
    829: bytes.fromhex("b3bda89bb233f019ffffffffffffffff7d030000000000000500000001000000b9cc3500b9cc35860000000001000000"),
    830: bytes.fromhex("a9f0bd23ae4b169ace5cd6c7ce5cd6c77b03000000000000a50000000100000003d9520003d9525a0000000001000000"),
    831: bytes.fromhex("fe59255ffcb24abf30730f1909a88bd53b0300000000000078a3000001009b00a5000000010000000000000001000000"),
    832: bytes.fromhex("a8a2abb2a6adacdfd5fcc12d36ca56413b030000000000008a00000001000000f08d4700f6dd78740000000001000000"),
    833: bytes.fromhex("a5ad26fca5ad26fcdee7dc1fc7479b37bb0200000000000054000000010000005d000000010000000000000001000000"),
}


SCENARIOS = [
    (784, "scn00_00"),
    (785, "scn00_01"),
    (786, "scn00_02"),
    (787, "scn00_03"),
    (788, "scn00_04"),
    (789, "scn00_05"),
    (790, "scn00_06"),
    (791, "scn00_07"),
    (792, "scn00_08"),
    (793, "scn00_09"),
    (794, "scn00_10"),
    (795, "scn00_11"),
    (796, "scn00_12"),
    (797, "scn00_13"),
    (798, "scn00_14"),
    (799, "scn00_15"),
    (800, "scn00_16"),
    (801, "scn00_17"),
    (802, "scn00_18"),
    (803, "scn00_19"),
    (804, "scn00_20"),
    (805, "scn00_21"),
    (806, "scn00_22"),
    (807, "scn00_23"),
    (808, "scn00_24"),
    (809, "scn00_25"),
    (810, "scn00_26"),
    (811, "scn00_27"),
    (812, "scn00_28"),
    (813, "scn00_29"),
    (814, "scn00_30"),
    (815, "scn00_31"),
    (816, "scn00_32"),
    (817, "scn00_33"),
    (818, "scn00_34"),
    (819, "scn00_35"),
    (820, "scn00_36"),
    (821, "scn00_37"),
    (822, "scn00_38"),
    (823, "scn00_39"),
    (824, "scn00_40"),
    (825, "scn00_41"),
    (826, "scn00_42"),
    (827, "scn00_43"),
    (828, "scn00_44"),
    (829, "scn00_45"),
    (830, "scn00_46"),
    (831, "scn00_47"),
    (832, "scn00_48"),
    (833, "scn01_01"),
]

# Helper XOR cipher implementation matching Frontwing HXV4 specification
class FilterBoundary:
    __slots__ = ("pos0", "pos1", "key", "byte0", "byte1")
    def __init__(self, pos0: int, pos1: int, key: int, byte0: int, byte1: int):
        self.pos0 = pos0
        self.pos1 = pos1
        self.key = key
        self.byte0 = byte0
        self.byte1 = byte1

class FilterRuntimeState:
    def __init__(self, seed_state: bytes) -> None:
        if len(seed_state) != 48:
            raise ValueError(f"filter seed state must be 48 bytes, got {len(seed_state)}")
        null_mode = bool(seed_state[45])
        self.boundary0 = self._init_boundary(struct.unpack_from("<Q", seed_state, 0)[0], null_mode)
        self.boundary1 = self._init_boundary(struct.unpack_from("<Q", seed_state, 8)[0], null_mode)
        self.split_offset = struct.unpack_from("<Q", seed_state, 16)[0]
        has_bulk = bool(seed_state[44])
        self.bulk_key = seed_state[24:40] if has_bulk else b""

    @staticmethod
    def _init_boundary(value: int, null_mode: bool) -> FilterBoundary:
        pos0 = (value >> 48) & 0xFFFF
        pos1 = (value >> 32) & 0xFFFF
        if pos0 == pos1:
            pos1 += 1
        key_byte = value & 0xFF
        byte0 = (value >> 8) & 0xFF
        byte1 = (value >> 16) & 0xFF
        if key_byte == 0:
            key_byte = 0 if null_mode else 0xA5
        return FilterBoundary(pos0, pos1, key_byte * 0x01010101, byte0, byte1)

    def _apply_boundary(self, data: bytearray, b: FilterBoundary, chunk_start: int, buf_start: int, size: int):
        for i in range(size):
            shift = ((chunk_start + i) & 3) * 8
            data[buf_start + i] ^= (b.key >> shift) & 0xFF
        p0 = b.pos0 - chunk_start
        if b.byte0 and 0 <= p0 < size:
            data[buf_start + p0] ^= b.byte0
        p1 = b.pos1 - chunk_start
        if b.byte1 and 0 <= p1 < size:
            data[buf_start + p1] ^= b.byte1

    def apply(self, data: bytearray, offset: int = 0) -> bool:
        if not data:
            return False
        size = len(data)
        end = offset + size
        if self.bulk_key and offset < len(self.bulk_key):
            for i in range(max(offset, 0), min(end, len(self.bulk_key))):
                data[i - offset] ^= self.bulk_key[i]
        split = self.split_offset
        if split <= offset:
            self._apply_boundary(data, self.boundary1, offset, 0, size)
        elif split < end:
            s1 = split - offset
            self._apply_boundary(data, self.boundary0, offset, 0, s1)
            self._apply_boundary(data, self.boundary1, split, s1, end - split)
        else:
            self._apply_boundary(data, self.boundary0, offset, 0, size)
        return True

def calc_adler32(data: bytes) -> int:
    return zlib.adler32(data) & 0xFFFFFFFF

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

class PatcherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("COCORO - Cài Đặt Patch Việt Hóa (Bản Full)")
        self.geometry("660x500")
        self.minsize(580, 420)
        self.configure(bg="#F4F6F9")

        self.base_dir = get_base_dir()
        self.patch_data_dir = self.base_dir / "patch_data"
        if not self.patch_data_dir.exists():
            dev_candidate = self.base_dir / "patch_data"
            if dev_candidate.exists():
                self.patch_data_dir = dev_candidate

        self.setup_ui()
        self.auto_detect_game_path()

    def setup_ui(self):
        # Header Frame
        header = tk.Frame(self, bg="#2C3E50", height=65)
        header.pack(fill="x")
        
        lbl_title = tk.Label(header, text="COCORO — BẢN VIỆT HÓA CHÍNH THỨC", font=("Segoe UI", 14, "bold"), fg="#ECF0F1", bg="#2C3E50")
        lbl_title.pack(pady=(10, 2))
        lbl_sub = tk.Label(header, text="Trình cài đặt tự động 50 Chương kịch bản (12.867 câu thoại) + Toàn bộ UI Việt hóa", font=("Segoe UI", 9), fg="#BDC3C7", bg="#2C3E50")
        lbl_sub.pack(pady=(0, 10))

        # Main Body
        body = tk.Frame(self, bg="#F4F6F9", padx=15, pady=15)
        body.pack(fill="both", expand=True)

        # Folder Selection Frame
        lbl_folder = tk.Label(body, text="Thư mục cài đặt game COCORO:", font=("Segoe UI", 10, "bold"), bg="#F4F6F9", anchor="w")
        lbl_folder.pack(fill="x", pady=(0, 5))

        f_entry = tk.Frame(body, bg="#F4F6F9")
        f_entry.pack(fill="x", pady=(0, 5))

        self.var_path = tk.StringVar()
        self.entry_path = ttk.Entry(f_entry, textvariable=self.var_path, font=("Segoe UI", 9))
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.var_path.trace_add("write", lambda *args: self.validate_path())

        btn_browse = ttk.Button(f_entry, text="Chọn thư mục...", command=self.browse_folder)
        btn_browse.pack(side="right")

        self.lbl_status = tk.Label(body, text="", font=("Segoe UI", 9), bg="#F4F6F9", anchor="w")
        self.lbl_status.pack(fill="x", pady=(0, 10))

        # Buttons Frame
        btn_frame = tk.Frame(body, bg="#F4F6F9")
        btn_frame.pack(fill="x", pady=(5, 12))

        self.btn_install = tk.Button(
            btn_frame, text="CÀI ĐẶT VIỆT HÓA", font=("Segoe UI", 10, "bold"),
            bg="#27AE60", fg="white", activebackground="#219150", activeforeground="white",
            relief="flat", padx=18, pady=9, cursor="hand2", command=self.start_install
        )
        self.btn_install.pack(side="left", padx=(0, 10))

        self.btn_restore = tk.Button(
            btn_frame, text="Khôi phục bản gốc", font=("Segoe UI", 9),
            bg="#E67E22", fg="white", activebackground="#D35400", activeforeground="white",
            relief="flat", padx=14, pady=9, cursor="hand2", command=self.start_restore
        )
        self.btn_restore.pack(side="left")

        # Progress bar
        self.progress = ttk.Progressbar(body, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(0, 10))

        # Log box
        lbl_log = tk.Label(body, text="Nhật ký hoạt động:", font=("Segoe UI", 9, "bold"), bg="#F4F6F9", anchor="w")
        lbl_log.pack(fill="x", pady=(0, 2))

        self.txt_log = tk.Text(body, height=10, font=("Consolas", 9), bg="white", relief="solid", bd=1)
        self.txt_log.pack(fill="both", expand=True)

    def log(self, text: str):
        self.txt_log.insert("end", text + "\n")
        self.txt_log.see("end")

    def auto_detect_game_path(self):
        candidates = [
            Path(r"E:\Games\COCORO.FIXED\game"),
            Path(r"D:\Games\COCORO.FIXED\game"),
            Path(r"C:\Games\COCORO.FIXED\game"),
            Path(r"E:\SteamLibrary\steamapps\common\COCORO"),
            Path(r"D:\SteamLibrary\steamapps\common\COCORO"),
            Path(r"C:\Program Files (x86)\Steam\steamapps\common\COCORO"),
            Path(r"C:\SteamLibrary\steamapps\common\COCORO"),
            Path(r"E:\SteamLibrary\steamapps\common\COCORO Demo"),
            self.base_dir,
            self.base_dir.parent,
        ]
        for c in candidates:
            if (c / "data.xp3").exists() and (
                (c / "COCORO.exe").exists() or 
                (c / "COCORO.exe.unpacked.exe").exists() or
                (c / "COCORO_Demo.exe").exists()
            ):
                self.var_path.set(str(c))
                self.log(f"[+] Tự động phát hiện thư mục game: {c}")
                return
        self.lbl_status.config(text="Vui lòng bấm 'Chọn thư mục...' để chọn folder chứa game COCORO", fg="#7F8C8D")

    def browse_folder(self):
        f = filedialog.askdirectory(title="Chọn thư mục game COCORO", initialdir=self.var_path.get() or "C:\\")
        if f:
            self.var_path.set(f)

    def validate_path(self) -> bool:
        p_str = self.var_path.get().strip()
        if not p_str:
            self.lbl_status.config(text="Chưa chọn thư mục game", fg="#7F8C8D")
            self.btn_install.config(state="disabled")
            self.btn_restore.config(state="disabled")
            return False
        p = Path(p_str)
        if (p / "data.xp3").exists():
            self.lbl_status.config(text="✓ Hợp lệ: Đã tìm thấy file data.xp3", fg="#27AE60")
            self.btn_install.config(state="normal")
            has_bak = (p / "data.xp3.original.bak").exists()
            self.btn_restore.config(state="normal" if has_bak else "disabled")
            return True
        else:
            self.lbl_status.config(text="✗ Chưa tìm thấy data.xp3 trong thư mục này", fg="#E74C3C")
            self.btn_install.config(state="disabled")
            self.btn_restore.config(state="disabled")
            return False

    def start_install(self):
        if not self.validate_path(): return
        self.btn_install.config(state="disabled")
        self.btn_restore.config(state="disabled")
        threading.Thread(target=self._run_install, daemon=True).start()

    def start_restore(self):
        if not self.validate_path(): return
        self.btn_install.config(state="disabled")
        self.btn_restore.config(state="disabled")
        threading.Thread(target=self._run_restore, daemon=True).start()

    def _run_restore(self):
        game_dir = Path(self.var_path.get().strip())
        xp3_path = game_dir / "data.xp3"
        bak_path = game_dir / "data.xp3.original.bak"

        if not bak_path.exists():
            self.log("[-] Không tìm thấy file sao lưu data.xp3.original.bak")
            messagebox.showerror("Lỗi", "Không tìm thấy file sao lưu data.xp3.original.bak")
            self.validate_path()
            return

        try:
            self.log("[*] Đang khôi phục data.xp3 từ bản sao lưu...")
            shutil.copy2(bak_path, xp3_path)
            self.log("[+] Đã khôi phục bản gốc nguyên vẹn thành công!")
            messagebox.showinfo("Thành công", "Đã khôi phục file game về bản gốc thành công!")
        except Exception as e:
            self.log(f"[-] Lỗi khi khôi phục: {e}")
            messagebox.showerror("Lỗi", f"Không thể khôi phục (có thể game đang mở?):\n{e}")
        finally:
            self.validate_path()

    def _run_install(self):
        game_dir = Path(self.var_path.get().strip())
        xp3_path = game_dir / "data.xp3"
        bak_path = game_dir / "data.xp3.original.bak"

        try:
            # 1. Load manifest or fall back to SCENARIOS
            manifest_path = self.patch_data_dir / "patch_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                patch_entries = manifest["entries"]
                filter_states_map = {int(k): bytes.fromhex(v) for k, v in manifest["filter_states"].items()}
                total_items = len(patch_entries)
                self.log(f"[*] Tìm thấy manifest cấu hình gồm {total_items} mục (Kịch bản thoại + Giao diện UI TLG5).")
            else:
                patch_entries = [{"entry_id": eid, "type": "scenario", "file": f"{scn}.bin"} for eid, scn in SCENARIOS]
                filter_states_map = FILTER_STATES
                total_items = len(patch_entries)
                self.log(f"[*] Chế độ mặc định: {total_items} chương kịch bản thoại.")

            # Check files in patch_data_dir
            for item in patch_entries:
                fpath = self.patch_data_dir / item["file"]
                if not fpath.exists():
                    raise FileNotFoundError(f"Thiếu file dữ liệu {item['file']} trong {self.patch_data_dir}")

            # 2. Backup if needed
            if not bak_path.exists():
                self.log("[*] Đang sao lưu data.xp3 -> data.xp3.original.bak...")
                shutil.copy2(xp3_path, bak_path)
                self.log("[+] Đã tạo bản sao lưu an toàn thành công.")
            else:
                self.log("[+] Đã có sẵn bản sao lưu data.xp3.original.bak.")

            self.progress["value"] = 10

            # 3. Read XP3 index header
            self.log("[*] Đang đọc cấu trúc chỉ mục data.xp3...")
            with open(xp3_path, "rb") as f:
                f.seek(0, 2)
                old_file_size = f.tell()
                f.seek(0)
                hdr = f.read(0x30)
                hdr_offset = int.from_bytes(hdr[11:19], "little")
                resolved_index_offset = hdr_offset
                if hdr_offset == 0x17 and len(hdr) >= 0x28:
                    cand = int.from_bytes(hdr[0x20:0x28], "little")
                    if 0 < cand < old_file_size:
                        resolved_index_offset = cand

                f.seek(resolved_index_offset)
                flag = f.read(1)[0]
                if flag == 1:
                    comp_sz = int.from_bytes(f.read(8), "little")
                    orig_sz = int.from_bytes(f.read(8), "little")
                    cdata = f.read(comp_sz)
                    index_bytes = zlib.decompress(cdata)
                else:
                    raise ValueError(f"Unsupported XP3 index flag {flag}")

            self.progress["value"] = 30

            # 4. Encrypt all patch blobs
            self.log(f"[*] Đang mã hóa và chuẩn bị {total_items} mục dữ liệu...")
            encrypted_blobs = {}
            current_offset = old_file_size
            blobs_stream = bytearray()

            for step_idx, item in enumerate(patch_entries):
                entry_id = item["entry_id"]
                plain = (self.patch_data_dir / item["file"]).read_bytes()
                adler = calc_adler32(plain)

                st_bytes = filter_states_map[entry_id]
                filter_state = FilterRuntimeState(st_bytes)
                cipher = bytearray(plain)
                filter_state.apply(cipher, 0)

                encrypted_blobs[entry_id] = {
                    "offset": current_offset,
                    "size": len(cipher),
                    "adler32": adler,
                }
                blobs_stream.extend(cipher)
                current_offset += len(cipher)
                prog_val = 30 + int((step_idx + 1) / total_items * 40)
                self.progress["value"] = prog_val

            self.log(f"   + Đã mã hóa xong toàn bộ {total_items} mục ({len(blobs_stream):,} bytes)")
            self.progress["value"] = 75

            # 5. Update index buffer
            self.log("[*] Cập nhật bảng chỉ mục XP3...")
            index_buf = bytearray(index_bytes)
            cursor = 0
            entry_idx = 0
            while cursor + 12 <= len(index_buf):
                tag = index_buf[cursor:cursor+4]
                sz = int.from_bytes(index_buf[cursor+4:cursor+12], "little")
                chunk_end = cursor + 12 + sz

                if tag == b"File":
                    if entry_idx in encrypted_blobs:
                        info = encrypted_blobs[entry_idx]
                        sub = cursor + 12
                        while sub + 12 <= chunk_end:
                            sub_tag = index_buf[sub:sub+4]
                            sub_sz = int.from_bytes(index_buf[sub+4:sub+12], "little")
                            b_start = sub + 12
                            sub += 12 + sub_sz

                            if sub_tag == b"adlr":
                                struct.pack_into("<I", index_buf, b_start, info["adler32"])
                            elif sub_tag == b"segm":
                                struct.pack_into("<QQQ", index_buf, b_start + 4, info["offset"], info["size"], info["size"])
                            elif sub_tag in (b"Info", b"info"):
                                struct.pack_into("<QQ", index_buf, b_start + 4, info["size"], info["size"])
                    entry_idx += 1
                cursor = chunk_end

            self.progress["value"] = 85

            # 6. Compress and append new index
            self.log("[*] Đang ghi dữ liệu vào data.xp3...")
            comp_new_index = zlib.compress(bytes(index_buf), level=9)
            new_index_offset = current_offset
            index_block = bytearray()
            index_block.append(0x01)
            index_block.extend(len(comp_new_index).to_bytes(8, "little"))
            index_block.extend(len(index_buf).to_bytes(8, "little"))
            index_block.extend(comp_new_index)

            with open(xp3_path, "r+b") as f:
                f.seek(old_file_size)
                f.write(blobs_stream)
                f.write(index_block)
                f.seek(0x20)
                f.write(new_index_offset.to_bytes(8, "little"))
                f.flush()

            self.progress["value"] = 100
            self.log("[+] CÀI ĐẶT THÀNH CÔNG RỰC RỠ 100%!")
            self.log("[+] Hãy mở game và chọn ngôn ngữ 'English' để chơi tiếng Việt.")
            messagebox.showinfo(
                "Cài Đặt Thành Công",
                "Đã cài đặt bản dịch Tiếng Việt trọn vẹn cho COCORO thành công 100%!\n\n"
                "Cách chơi:\n"
                "1. Khởi động game bình thường qua Steam hoặc file COCORO.exe.\n"
                "2. Trong phần cài đặt ngôn ngữ (Config -> Language), chọn 'English' để hiển thị toàn bộ tiếng Việt!"
            )
        except Exception as e:
            self.log(f"[-] Lỗi trong quá trình cài đặt: {e}")
            messagebox.showerror("Lỗi", f"Quá trình cài đặt gặp lỗi (hãy đảm bảo game đã tắt):\n{e}")
        finally:
            self.validate_path()

def main():
    app = PatcherApp()
    app.mainloop()

if __name__ == "__main__":
    main()
