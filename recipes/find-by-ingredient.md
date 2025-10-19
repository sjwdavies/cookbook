# Find by ingredient

<script>
async function loadData() {
  const res = await fetch('/recipes/ingredients.json').catch(()=>fetch('ingredients.json'));
  const data = await res.json();
  return data;
}
function render(list){
  const out = document.getElementById('results');
  out.innerHTML='';
  list.forEach(item=>{
    const li=document.createElement('li');
    const a=document.createElement('a');
    a.href=item.path; a.textContent=item.title;
    li.appendChild(a); out.appendChild(li);
  });
}
document.addEventListener('DOMContentLoaded', async () => {
  const data = await loadData();
  const input = document.getElementById('q');
  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    const hits = data.filter(r => r.ingredients.join(' ').toLowerCase().includes(q));
    render(hits.slice(0,100));
  });
});
</script>
<input id="q" placeholder="e.g., chicken, lemon"></input>
<ul id="results"></ul>
