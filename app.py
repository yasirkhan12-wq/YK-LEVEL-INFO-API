import os
from datetime import datetime
import json
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import Flask, jsonify, request
import requests
import urllib3
import pApaX_pb2

urllib3.disable_warnings()

app = Flask(__name__)
app.json.sort_keys = False



IND_ACCOUNTS = [
    {"uid": "8009779890", "password": "JCD_5FD6B0EB6ECDC3A7"},
]
# ADD YOUR LEVEL 3+ GUEST ACCOUNT 
OTHARS_ACCOUNTS = [
    {"uid": "4294579067", "password": "8AB472D775EE9E6EA7BC980C564E980ED5D5CD007FB475213E7966CED5436E33"},
    {"uid": "4292718504", "password": "10B5AFDB25DDE05CBCAB246715C7F23587B328991B56955DA40EF65405EA6EF6"},
]

# Region configurations mapping
REGION_CONFIGS = {}

# Map IND region
for acc in IND_ACCOUNTS:
  REGION_CONFIGS["IND"] = {
      "uid": acc["uid"],
      "password": acc["password"],
      "client_url": "https://client.ind.freefiremobile.com",
  }

# Map other priority regions to OTHARS accounts
PRIORITY_REGIONS = [
    "BD", "SG", "TH", "PK", "VN", "ID", "TW", "BR", "EU", "RU", "TR", "ME", "NA", "SAC", "US"
]

for i, reg in enumerate(PRIORITY_REGIONS):
  acc = OTHARS_ACCOUNTS[i % len(OTHARS_ACCOUNTS)]
  REGION_CONFIGS[reg] = {
      "uid": acc["uid"],
      "password": acc["password"],
      "client_url": "https://clientbp.ggpolarbear.com",
  }

# Ensure IND is explicitly covered
if "IND" not in REGION_CONFIGS and IND_ACCOUNTS:
  REGION_CONFIGS["IND"] = {
      "uid": IND_ACCOUNTS[0]["uid"],
      "password": IND_ACCOUNTS[0]["password"],
      "client_url": "https://client.ind.freefiremobile.com",
  }

_3K = b"Yg&tc%DEuh6%Zc^8"
_4V = b"6oyZDr22E3ychjM%"
_6T = 15
_7H = {"Content-Type": "application/x-www-form-urlencoded"}
_8A = "Dalvik/2.1.0 (Linux; U; Android 11)"
_9R = "v1 1"
_10L = "OB55"

os.environ["FLASK_DEBUG"] = "0"
os.environ["FLASK_ENV"] = "production"
TOKEN_CACHE = {"token": {}, "expiry_time": {}}

# Protobuf  Payload
Payload_data = (
 "0a04080110000a04080210300a05080310ca010a05080410a0040a05080510f4070a05080610b40e0a05080710e8150a05080810d81d0a0508091086260a05080a10f42e0a05080b1098380a05080c1096420a05080d10a04c0a05080e1084570a05080f1090620a05081010ec6d0a05081110fa790a06081210c886010a06081310d693010a0608141098a1010a0608151098af010a06081610d6bd010a06081710d0cc010a0608181086dc010a06081910f8eb010a06081a10a6fc010a06081b108c8d020a06081c10aca7020a06081d10bac2020a06081e10c6de020a06081f10c6fb020a0608201092a1030a06082110eec9030a06082210e0f4030a06082310eaa2040a06082410acd5040a06082510b28c050a06082610f8c7050a06082710fa87060a06082810bccc060a06082910d0aa070a06082a10d690080a06082b109080090a06082c108cf7090a06082d10b8f70a0a06082e10dcff0b0a06082f10f4990d0a06083010fcaf0e0a06083110f2d70f0a060832108cc4100a06083310b8c7120a060834109ea1150a06083510e68d180a060836108c8d1b0a06083710949f1e0a06083810f4c3210a060839109cd7260a06083a10d0862c0a06083b1098d2310a06083c10eab9370a06083d109ac83f0a06083e10c085480a06083f10d4f1500a06084010d88c5a0a06084110fcdf630a06084210b2ae700a06084310a2947d0a070844109a9e8b010a07084510c0bf99010a070846109aa7a8010a07084710b2deba010a07084810fce9cd010a0708491080e6e1010a07084a10c6d2f6010a07084b10caaf8c020a07084c10b0dfa6020a07084d10fc96c1020a07084e1090abdf020a07084f108cc7fd020a07085010aea39e030a07085110ccc2c2030a0708521092f5ea030a07085310d69e96040a0708541098bfc4040a0708551086d2f5040a0708561086a7b0050a07085710a49dee050a07085810b0b9af060a07085910aafbf3060a07085a10f29cbb070a07085b10949d8f080a07085c1088a4e6080a07085d10a08fc1090a07085e10bac79f0a0a07085f10b2d4810b0a0708601082b6e70b0a07086110acadcb0c0a07086210ccf7bd0d0a07086310b6d0ae0e0a070864109c8ca30f"
)

# Helper function to decode protobuf varint
def _decode_varint(data, pos):
  val = 0
  shift = 0
  while True:
    b = data[pos]
    pos += 1
    val |= (b & 0x7f) << shift
    if not (b & 0x80):
      break
    shift += 7
  return val, pos

# Dynamic parser to decode pAyLOaD_HEX into pAyLOaD dictionary
def LOad_pAyLoaD_daTa(hex_str):
  data = bytes.fromhex(hex_str)
  table = {}
  pos = 0
  while pos < len(data):
    tag = data[pos]
    pos += 1
    if tag == 0x0a:
      length, pos = _decode_varint(data, pos)
      end_pos = pos + length
      level = 0
      exp = 0
      while pos < end_pos:
        field_tag = data[pos]
        pos += 1
        if field_tag == 0x08:  
          level, pos = _decode_varint(data, pos)
        elif field_tag == 0x10:  
          exp, pos = _decode_varint(data, pos)
        else:
          break
      if level:
        table[level] = exp
    else:
      break
  return table

pAyLOaD = LOad_pAyLoaD_daTa(Payload_data)


def YoUr_MoM(d):
  return AES.new(_3K, AES.MODE_CBC, _4V).encrypt(pad(d, 16))


def UNknown(d):
  try:
    cipher = AES.new(_3K, AES.MODE_CBC, _4V)
    decrypted = cipher.decrypt(d)
    return unpad(decrypted, 16)
  except Exception:
    try:
      return cipher.decrypt(d)
    except Exception:
      return d


def ReSPeCt_GiRLs(n):
  res = bytearray()
  while n >= 0x80:
    res.append((n & 0x7f) | 0x80)
    n >>= 7
  res.append(n)
  return bytes(res)


def YOuR_FaThER(uid):
  return YoUr_MoM(b"\x08" + ReSPeCt_GiRLs(int(uid)))


def Get_Or_Refresh_Token(reg_key, cfg):
  current_time = time.time()
  if not TOKEN_CACHE["token"].get(reg_key) or current_time >= TOKEN_CACHE[
      "expiry_time"
  ].get(reg_key, 0):
    url = f"https://ff-jwt-gen-api.lovable.app/api/public/token?uid={cfg['uid']}&password={cfg['password']}"
    try:
      r = requests.get(url, timeout=_6T)
      if r.status_code == 200:
        token = r.json().get("token")
        if token:
          TOKEN_CACHE["token"][reg_key] = token
          TOKEN_CACHE["expiry_time"][reg_key] = current_time + (8 * 3600)
          return TOKEN_CACHE["token"][reg_key]
    except Exception:
      return None
  return TOKEN_CACHE["token"].get(reg_key)


def calculate_level_progression(current_level, current_exp):
  next_level = current_level + 1
  
  current_level_base_exp = pAyLOaD.get(current_level, 0)
  next_level_total_exp = pAyLOaD.get(next_level, pAyLOaD.get(100, 32032284))
  
  exp_needed_for_next = next_level_total_exp - current_level_base_exp
  exp_gained_in_current = current_exp - current_level_base_exp
  
  if exp_gained_in_current < 0:
    exp_gained_in_current = 0

  if current_level >= 100:
    return {
        "next_level": 100,
        "next_level_exp": pAyLOaD.get(100, 32032284),
        "next_level_exp_need": 0,
        "total_processing": "100.00%"
    }

  next_level_exp_need = next_level_total_exp - current_exp
  if next_level_exp_need < 0:
    next_level_exp_need = 0

  if exp_needed_for_next > 0:
    percentage = (exp_gained_in_current / exp_needed_for_next) * 100
    if percentage > 100:
      percentage = 100.0
    elif percentage < 0:
      percentage = 0.0
    total_processing = f"{percentage:.2f}%"
  else:
    total_processing = "100.00%"

  return {
      "next_level": next_level,
      "next_level_exp": next_level_total_exp,
      "next_level_exp_need": next_level_exp_need,
      "total_processing": total_processing
  }


def parse_with_pApaX_pb2(raw_bytes, reg_key):
  response = pApaX_pb2.PlayerResponse()
  try:
    response.ParseFromString(raw_bytes)
    info = response.player_info
    
    if not info.uid:
      brief = pApaX_pb2.PlayerBriefInfo()
      brief.ParseFromString(raw_bytes)
      if brief.uid:
        info = brief

    level = info.level
    exp = info.exp
    progression = calculate_level_progression(level, exp)
    oB_vErSioN = _10L

    return {
        "Nickname": info.nickname,
        "uid": info.uid,
        "Exp": exp,
        "Next_level_exp": progression["next_level_exp"],
        "Region": info.region if info.region else reg_key,
        "Level": level,
        "Next_level": progression["next_level"],
        "Next_level_exp_need": progression["next_level_exp_need"],
        "Total_prossing": progression["total_processing"],
        "OB_Version": oB_vErSioN
    }
  except Exception as e:
    print(f"Protobuf parse error: {e}")
    return None


@app.route("/level-info", methods=["GET", "POST"])
def get_player_personal_show():
  if request.method == "POST":
    req_data = request.get_json(silent=True) or {}
    target_region = req_data.get("region") or request.form.get("region")
    target_uid = req_data.get("uid") or request.form.get("uid")
  else:
    target_region = request.args.get("region")
    target_uid = request.args.get("uid")

  if target_region:
    target_region = target_region.upper()
    if target_region not in REGION_CONFIGS:
      return (
          jsonify({
              "error": f"Invalid region '{target_region}'.",
              "supported_regions": list(REGION_CONFIGS.keys()),
          }),
          400,
      )
    regions_to_check = {target_region: REGION_CONFIGS[target_region]}
  else:
    regions_to_check = REGION_CONFIGS

  for reg_key, cfg in regions_to_check.items():
    jwt = Get_Or_Refresh_Token(reg_key, cfg)
    if not jwt:
      continue

    headers = {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": _7H["Content-Type"],
        "User-Agent": _8A,
        "X-GA": _9R,
        "ReleaseVersion": _10L,
        "Connection": "Keep-Alive",
    }
    client_url = cfg["client_url"]
    query_uid = target_uid if target_uid else cfg["uid"]

    try:
      main_payload = YOuR_FaThER(query_uid)
      target_endpoint = f"{client_url}/GetPlayerBriefInfo"

      main_resp = requests.post(
          target_endpoint,
          headers=headers,
          data=main_payload,
          timeout=_6T,
          verify=False,
      )

      if main_resp.status_code == 200:
        raw_content = main_resp.content
        if len(raw_content) == 0:
          continue

        target_data = UNknown(raw_content)

        parsed_result = parse_with_pApaX_pb2(target_data, reg_key)
        if parsed_result and parsed_result.get("uid") != 0:
          return jsonify(parsed_result), 200

    except Exception:
      continue

  return (
      jsonify({
          "error": "No data found 404"
      }),
      404,
  )


@app.route("/", methods=["GET", "POST"])
def root():
    return jsonify({
        "status": "online",
        "message": "Ff Player Level Info Api OB55",

        "api": {
            "name": "FF Player Level Info API",
            "version": "1.07",
            "ff_version": "OB55",
            "status": "stable"
        },

        "developer": {
            "name": "@XEROX_MODS",
            "project": "Player Level Info"
        },

        "endpoints": {
            "home": "/",
            "level_info": "/level-info?uid={UID}",
            "level_info_region": "/level-info?region=BD&uid={UID}"
        },

        "method": {
            "home": ["GET", "POST"],
            "level_info": ["GET", "POST"]
        },

        "supported_regions": [
            "IND", "BD", "SG", "TH", "PK",
            "VN", "ID", "TW", "BR", "EU",
            "RU", "TR", "ME", "NA", "SAC", "US"
        ]
    }), 200

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080, debug=True)
