import os
import json
import re
from pathlib import Path

# Folders
INPUT_DIR = Path("Cookies")
OUTPUT_DIR = Path("ConvertedCookies")
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Internal format names
FORMATS_INTERNAL = ["json", "netscape", "mozilla", "selenium"]
# Display names
FORMATS_DISPLAY = ["Json", "NetScape", "Mozilla", "Selenium"]

def detectar_formato(texto):
    texto = texto.strip()
    try:
        data = json.loads(texto)
        if isinstance(data, list) and all(isinstance(c, dict) for c in data):
            return "json", data
    except json.JSONDecodeError:
        pass

    if texto.startswith("# Netscape HTTP Cookie File"):
        cookies = []
        for line in texto.splitlines():
            if line.strip() and not line.startswith("#"):
                parts = line.split("\t")
                if len(parts) == 7:
                    try:
                        cookie = {
                            "domain": parts[0],
                            "flag": parts[1],
                            "path": parts[2],
                            "secure": parts[3] == "TRUE",
                            "expires": int(parts[4]) if parts[4].isdigit() else 0,
                            "name": parts[5],
                            "value": parts[6]
                        }
                        cookies.append(cookie)
                    except Exception:
                        continue
        return "netscape", cookies

    if re.search(r"domain=.*?;", texto):
        cookies = []
        for line in texto.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parts = line.split(";")
                name_value = parts[0].strip()
                if "=" not in name_value:
                    continue
                name, value = name_value.split("=", 1)
                domain = ""
                path = "/"
                expires = 0
                for p in parts[1:]:
                    p = p.strip()
                    if p.startswith("domain="):
                        domain = p[len("domain="):]
                    elif p.startswith("path="):
                        path = p[len("path="):]
                    elif p.startswith("expires="):
                        try:
                            expires = int(p[len("expires="):])
                        except:
                            expires = 0

                cookies.append({
                    "name": name,
                    "value": value,
                    "domain": domain,
                    "path": path,
                    "expires": expires,
                    "secure": False
                })
            except Exception:
                continue
        if cookies:
            return "mozilla", cookies

    return "unknown", []

def salvar_cookie(data, file_name, formato, extensao):
    output_path = OUTPUT_DIR / f"{file_name}.{formato}.{extensao.lstrip('.')}"
    with open(output_path, "w", encoding="utf-8") as f:
        if formato in ["json", "selenium"]:
            json.dump(data, f, indent=2, ensure_ascii=False)
        elif formato == "netscape":
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in data:
                domain = cookie.get('domain', '')
                flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                path = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                expires = int(cookie.get('expires', 0))
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                if not name or not value:
                    continue
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
        elif formato == "mozilla":
            for cookie in data:
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                domain = cookie.get('domain', '')
                path = cookie.get('path', '/')
                expires = cookie.get('expires', 0)
                if not name or not value:
                    continue
                f.write(f"{name}={value}; domain={domain}; path={path}; expires={expires}\n")
    print(f"{file_name} converted successfully to {formato} with extension {extensao}.")

def menu_formatos():
    print("Choose the format for conversion:")
    for i, fmt in enumerate(FORMATS_DISPLAY):
        print(f"[{i+1}] {fmt}")
    while True:
        try:
            choice = int(input("Enter the corresponding number: "))
            if 1 <= choice <= len(FORMATS_INTERNAL):
                return FORMATS_INTERNAL[choice - 1]
        except ValueError:
            pass
        print("Invalid choice, please try again.")

def menu_extensoes():
    options = ["Txt", "Json", "Cookies", "Dat", "Custom"]
    print("\nChoose the file extension for the output files:")
    for i, ext in enumerate(options):
        print(f"[{i+1}] {ext}")
    while True:
        try:
            choice = int(input("Enter the corresponding number: "))
            if 1 <= choice <= len(options):
                if options[choice - 1] == "custom":
                    custom_ext = input("Enter custom extension (without dot): ").strip()
                    if custom_ext and all(c.isalnum() for c in custom_ext):
                        return custom_ext
                    else:
                        print("Invalid extension, please try again.")
                else:
                    return options[choice - 1]
        except ValueError:
            pass
        print("Invalid choice, please try again.")

def main():
    arquivos = list(INPUT_DIR.glob("*"))
    if not arquivos:
        print("No cookie files found in 'cookies/'")
        return

    cookies_detectados = []

    print("Detecting cookie file formats:", end=" ")
    for i, arquivo in enumerate(arquivos):
        texto = arquivo.read_text(encoding="utf-8", errors="ignore")
        formato_detectado, cookies = detectar_formato(texto)
        print(f"{arquivo.name} ({formato_detectado})", end="\n" if i == len(arquivos) - 1 else ", ")
        if formato_detectado != "unknown" and cookies:
            cookies_detectados.append((arquivo.stem, cookies))

    if not cookies_detectados:
        print("No recognized cookie formats were found or cookies are empty.")
        return

    output_format = menu_formatos()
    output_extension = menu_extensoes()

    for file_name, cookies in cookies_detectados:
        salvar_cookie(cookies, file_name, output_format, output_extension)

    print("\nConversion completed. Check the files in 'ConvertedCookies'.")

if __name__ == "__main__":
    main()
