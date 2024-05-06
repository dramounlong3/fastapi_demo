async function submitForm(event) {
  event.preventDefault(); // 防止表單默認提交行為

  const form = document.querySelector(".form");
  const formData = new FormData(form);

  //   console.log("jifjijfiejkl");

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      console.log("第1段");
      const data = await response.json(); // 解析 JSON 格式的回傳訊息
      const messageDiv = document.querySelector(".message");
      messageDiv.textContent = JSON.stringify(data, null, 2); // 將回傳訊息美化並顯示在 messageDiv 元素中
    } else {
      //   console.log("第2段");
      const errorMessage = await response.text(); // 解析文本格式的錯誤信息
      //   console.error("Upload failed:", errorMessage);
      console.log(`test bad request ${typeof errorMessage}`);
      const responseObject = JSON.parse(errorMessage);
      console.log(`typeof responseObject ${typeof responseObject}`);
      console.log(
        `responseObject.detail.jsss ${typeof responseObject.detail.jsss}`
      );
      const messageDiv = document.querySelector(".message");
      //   messageDiv.textContent = errorMessage; // 將錯誤信息顯示在 messageDiv 元素中
      const jsssObj = JSON.parse(responseObject.detail.jsss);
      messageDiv.textContent = jsssObj.username;
    }
  } catch (error) {
    console.log("第3段");
    console.error("Error during upload:", error);
  }
}
