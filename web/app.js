const search = document.querySelector("#search");
const inventory = document.querySelector("#inventory");
const inventoryStatus = document.querySelector("#inventory-status");
const fields = ["symbol", "contract_account", "precision", "maximum_supply", "on_chain_status", "notes"];

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error);
  }
  return result;
}

async function showInventory() {
  try {
    const tokens = await fetchJson("/api/inventory");
    function render() {
      const query = search.value.trim().toLowerCase();
      const matches = tokens.filter(token =>
        [token.symbol, token.contract_account].some(value => value?.toLowerCase().includes(query))
      );
      const rows = matches.map(token => {
        const row = document.createElement("tr");
        for (const field of fields) {
          const cell = row.insertCell();
          cell.textContent = token[field] ?? "—";
        }
        return row;
      });
      inventory.replaceChildren(...rows);
      inventoryStatus.textContent = matches.length ? `${matches.length} of ${tokens.length} tokens` : "No matching tokens.";
    }
    search.addEventListener("input", render);
    render();
  } catch (error) {
    inventoryStatus.textContent = error.message;
  }
}

const form = document.querySelector("#factory-form");
const submit = form.querySelector("button");
const planStatus = document.querySelector("#plan-status");
const plan = document.querySelector("#plan");
const inventoryReview = document.querySelector("#inventory-review");
const downloadPlan = document.querySelector("#download-plan");

form.addEventListener("submit", async event => {
  event.preventDefault();
  const config = Object.fromEntries(new FormData(form));
  config.precision = Number(config.precision);
  config.chain = "proton-test";
  config.issuer = config.contract_account;
  submit.disabled = true;
  plan.hidden = true;
  inventoryReview.hidden = true;
  downloadPlan.hidden = true;
  if (downloadPlan.hasAttribute("href")) {
    URL.revokeObjectURL(downloadPlan.href);
    downloadPlan.removeAttribute("href");
  }
  planStatus.textContent = "Generating review plan…";
  try {
    const result = await fetchJson("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    });
    const matchCount = result.inventory_matches.length;
    inventoryReview.textContent = matchCount
      ? `Warehouse records with symbol ${config.symbol}: ${matchCount}. Verify the chain, contract and issuer before creating or issuing.`
      : "No matching symbol in the warehouse. Check XPR testnet to confirm token availability.";
    inventoryReview.hidden = false;
    plan.textContent = result.plan;
    const reviewText = `# ${inventoryReview.textContent}\n${result.plan}\n`;
    downloadPlan.href = URL.createObjectURL(new Blob([reviewText], { type: "text/plain" }));
    downloadPlan.hidden = false;
    plan.hidden = false;
    planStatus.textContent = "Review plan generated.";
  } catch (error) {
    planStatus.textContent = error.message;
  } finally {
    submit.disabled = false;
  }
});

showInventory();
