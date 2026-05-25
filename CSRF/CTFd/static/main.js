function checkEarnAnswer(event) {
  event.preventDefault();

  const input = document.getElementById("earn-answer");
  const result = document.getElementById("earn-result");

  if (!input || !result) {
    return false;
  }

  if (input.value === "2") {
    result.textContent = "정답입니다. 하지만 실제로는 겨우 1 coin밖에 벌 수 없을 것 같습니다.";
  } else {
    result.textContent = "오답입니다.";
  }

  return false;
}