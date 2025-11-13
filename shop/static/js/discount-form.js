(function () {
  const form = document.getElementById("discount-form");
  const typeRadios = document.getElementsByName("discount_type");
  const valueInput = document.getElementById("id_value");
  const samplePrice = document.getElementById("sample-price");
  const previewDesc = document.getElementById("preview-desc");
  const previewResult = document.getElementById("preview-result");
  const startDate = document.getElementById("id_start_date");
  const endDate = document.getElementById("id_end_date");
  const cancelBtn = document.getElementById("cancel-btn");

  function getSelectedType() {
    for (const r of typeRadios) {
      if (r.checked) return r.value;
    }
    return typeRadios.length > 0 ? typeRadios[0].value : "fixed";
  }

  function formatCurrency(n) {
    return Number(n).toFixed(2) + " грн";
  }

  function updatePreview() {
    const type = getSelectedType();
    const v = parseFloat(valueInput && valueInput.value);
    const price = parseFloat(samplePrice.value) || 0;

    if (isNaN(v) || v <= 0) {
      if (previewDesc) {
        previewDesc.textContent =
          "Введіть коректне значення знижки та приклад ціни.";
      }
      if (previewResult) {
        previewResult.textContent = "";
      }
      return;
    }

    let finalPrice;
    if (type === "fixed") {
      finalPrice = price - v;
      if (previewDesc) {
        previewDesc.textContent = `Фіксована знижка ${v} грн застосована до ціни ${formatCurrency(
          price
        )}.`;
      }
    } else {
      finalPrice = price * (1 - v / 100);
      if (previewDesc) {
        previewDesc.textContent = `Знижка ${v}% застосована до ціни ${formatCurrency(
          price
        )}.`;
      }
    }

    if (finalPrice < 0) finalPrice = 0;
    if (previewResult) {
      previewResult.textContent = `Ціна після знижки: ${formatCurrency(
        finalPrice
      )}`;
    }
  }

  for (const r of typeRadios) {
    if (r) {
      r.addEventListener("change", updatePreview);
    }
  }

  if (valueInput) {
    valueInput.addEventListener("input", updatePreview);
  }

  if (samplePrice) {
    samplePrice.addEventListener("input", updatePreview);
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      const sVal = startDate && startDate.value;
      const eVal = endDate && endDate.value;

      if (sVal && eVal) {
        const s = new Date(sVal);
        const en = new Date(eVal);

        if (en <= s) {
          e.preventDefault();
          alert("Дата закінчення повинна бути пізнішою за дату початку.");
          return false;
        }
      }
    });
  }

  if (cancelBtn) {
    cancelBtn.addEventListener("click", function () {
      history.back();
    });
  }

  updatePreview();
})();
