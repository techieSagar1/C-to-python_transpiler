let cEditor = CodeMirror.fromTextArea(document.getElementById("c-code"), {
  mode: "text/x-csrc",
  theme: "monokai",
  lineNumbers: true,
  autofocus: true,
});

let pythonEditor = CodeMirror.fromTextArea(document.getElementById("python-code"), {
  mode: "python",
  theme: "monokai",
  lineNumbers: true,
  readOnly: true,
});

// Live conversion (every keystroke)
cEditor.on("change", async () => {
  const code = cEditor.getValue();

  if (code.trim() === "") {
    pythonEditor.setValue("");
    return;
  }

  const response = await fetch("/convert", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ code })
  });

  const result = await response.json();
  pythonEditor.setValue(result.python_code || "Error converting code.");
});
