let relevantCode = "Could not find loadChart function call.";
const scripts = document.querySelectorAll("script");
for (const script of scripts) {
  if (script.src) {
    try {
      const response = await fetch(script.src);
      const scriptContent = await response.text();
      if (scriptContent.includes("loadChart(")) {
        const lines = scriptContent.split("\n");
        const lineNumber = lines.findIndex((line) =>
          line.includes("loadChart(")
        );
        if (lineNumber !== -1) {
          relevantCode = lines.slice(lineNumber - 5, lineNumber + 5).join("\n");
          break;
        }
      }
    } catch (error) {
      // Ignore errors for external scripts that can't be fetched
    }
  } else if (script.textContent.includes("loadChart(")) {
    const lines = script.textContent.split("\n");
    const lineNumber = lines.findIndex((line) => line.includes("loadChart("));
    if (lineNumber !== -1) {
      relevantCode = lines.slice(lineNumber - 5, lineNumber + 5).join("\n");
      break;
    }
  }
}

data = {
  relevantCode: relevantCode,
};
