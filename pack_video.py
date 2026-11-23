# -*- coding: utf-8 -*-
"""
COCORO - Video Repacker (video.xp3)
- Hỗ trợ đóng gói video đã Việt hóa (WMV/ASF) vào video.xp3
- Áp dụng chuẩn mã hóa Frontwing HXV4 Filter Cipher (DripProgram)
- Tự động sao lưu video.xp3.original.bak
"""
import os
import sys
import struct
import zlib
import shutil
from pathlib import Path

# Thư viện giải mã Frontwing HXV4
sys.path.insert(0, r"E:\Extract Tools\cxdec-hxv4\src\common")
from xp3_inspect import DripProgram, read_archive, load_index, build_filter_state_map

ROOT_DIR = Path(r"D:\Software\Antigravity\Project\Cocoro")
VIDEOS_DIR = ROOT_DIR / "Exported_Videos"
GAME_DIR = Path(r"E:\Games\COCORO.FIXED\game")
VIDEO_XP3 = GAME_DIR / "video.xp3"
VIDEO_BAK = GAME_DIR / "video.xp3.original.bak"
DRIP_PATH = Path(r"E:\Extract Tools\cxdec-hxv4\data\static_recover\drip_program_COCORO.exe.unpacked.json")

# Bản đồ ánh xạ tên video vào Entry Index trong video.xp3
VIDEO_ENTRY_MAP = {
    "op.wmv": 1,
    "ed.wmv": 2,
    "ed2.wmv": 3,
    "ed2_en.wmv": 4,
    "ed2_cn.wmv": 5,
    "ed2_tw.wmv": 6,
}

def calc_adler32(data: bytes) -> int:
    return zlib.adler32(data) & 0xFFFFFFFF

def main():
    print("======================================================================")
    print("           COCORO - TRÌNH ĐÓNG GÓI VIDEO VIỆT HÓA (VIDEO.XP3)         ")
    print("======================================================================")

    if not VIDEO_XP3.exists():
        print(f"[-] Không tìm thấy file {VIDEO_XP3}!")
        return

    # 1. Tự động sao lưu bản gốc nếu chưa có
    if not VIDEO_BAK.exists():
        print(f"[*] Đang tạo bản sao lưu an toàn: {VIDEO_BAK.name}...")
        shutil.copy2(VIDEO_XP3, VIDEO_BAK)
        print("   + Đã tạo video.xp3.original.bak thành công.")
    else:
        print(f"[+] Đã có sẵn bản sao lưu gốc: {VIDEO_BAK.name}")

    # 2. Quét video cần thay thế từ thư mục Exported_Videos
    print(f"\n[*] Đang quét video mới từ: {VIDEOS_DIR}...")
    replacements = {}
    if VIDEOS_DIR.exists():
        for fn, entry_id in VIDEO_ENTRY_MAP.items():
            vp = VIDEOS_DIR / fn
            if vp.exists():
                replacements[entry_id] = (fn, vp)
                print(f"   + Tìm thấy video thay thế: {fn:12s} (Entry #{entry_id}, {vp.stat().st_size:,} bytes)")

    if not replacements:
        print("[-] Không tìm thấy video nào cần thay thế trong Exported_Videos/.")
        print("    Vui lòng đặt video tiếng Việt (chuẩn .wmv) vào Exported_Videos rồi chạy lại script.")
        return

    # 3. Tính toán khóa Filter Cipher từ DripProgram
    print("\n[*] Tính toán khóa giải mã HXV4 từ DripProgram...")
    drip = DripProgram.load(DRIP_PATH)
    with open(VIDEO_BAK, "rb") as f:
        blob = f.read()

    info, entries, _ = read_archive(VIDEO_BAK)
    _, _, _, index = load_index(blob)
    states = build_filter_state_map(blob, index, entries, drip)
    print(f"   + Đã dựng thành công khóa cho {len(states)} entry trong video.xp3.")

    # 4. Mã hóa và chuẩn bị blob video
    print("\n[*] Đang mã hóa dữ liệu video theo chuẩn HXV4...")
    old_file_size = VIDEO_BAK.stat().st_size
    current_offset = old_file_size
    blobs_stream = bytearray()
    encrypted_blobs = {}

    # Copy bản gốc sang file làm việc
    shutil.copy2(VIDEO_BAK, VIDEO_XP3)

    with open(VIDEO_XP3, "r+b") as out_f:
        out_f.seek(old_file_size)

        for entry_id, (fn, vp) in sorted(replacements.items()):
            print(f"   + Đang mã hóa và ghi {fn} (Entry #{entry_id})...")
            plain_data = vp.read_bytes()
            adler = calc_adler32(plain_data)

            fs = states[entry_id]
            cipher_data = bytearray(plain_data)
            fs.apply(cipher_data, 0)

            encrypted_blobs[entry_id] = {
                "offset": current_offset,
                "size": len(cipher_data),
                "adler32": adler
            }

            out_f.write(cipher_data)
            current_offset += len(cipher_data)
            print(f"     -> Ghi xong: {len(cipher_data):,} bytes tại offset 0x{encrypted_blobs[entry_id]['offset']:X}")

        # 5. Cập nhật chỉ mục XP3
        print("\n[*] Cập nhật chỉ mục lưu trữ XP3...")
        index_buf = bytearray(index)
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

        comp_new_index = zlib.compress(bytes(index_buf), level=9)
        new_index_offset = current_offset
        index_block = bytearray()
        index_block.append(0x01)
        index_block.extend(len(comp_new_index).to_bytes(8, "little"))
        index_block.extend(len(index_buf).to_bytes(8, "little"))
        index_block.extend(comp_new_index)

        # Ghi khối index mới và cập nhật con trỏ tại 0x20
        out_f.write(index_block)
        out_f.seek(0x20)
        out_f.write(new_index_offset.to_bytes(8, "little"))
        out_f.flush()

    print(f"\n[+] Hoàn tất! Dung lượng video.xp3 mới: {VIDEO_XP3.stat().st_size:,} bytes")
    print("======================================================================")
    print("              ĐÃ ĐÓNG GÓI VIDEO MỚI VÀO GAME THÀNH CÔNG!              ")
    print("======================================================================")

if __name__ == "__main__":
    main()
