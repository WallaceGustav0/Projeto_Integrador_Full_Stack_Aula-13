const api = "/api/reservas";
const $ = (seletor) => document.querySelector(seletor);

function dadosDoFormulario() {
  return {
    laboratorio: $("#laboratorio").value,
    data_reserva: $("#data-reserva").value,
    turno: $("#turno").value,
    responsavel: $("#responsavel").value,
    quantidade_pessoas: Number($("#quantidade").value),
    finalidade: $("#finalidade").value,
  };
}

async function lerResposta(resposta) {
  if (resposta.status === 204) return null;
  const corpo = await resposta.json();
  if (!resposta.ok) throw new Error(`${resposta.status}: ${corpo.detail ?? "Falha na requisição"}`);
  return corpo;
}

async function listar() {
  const parametros = new URLSearchParams();
  if ($("#filtro-laboratorio").value) parametros.set("laboratorio", $("#filtro-laboratorio").value);
  if ($("#filtro-turno").value) parametros.set("turno", $("#filtro-turno").value);
  const resposta = await fetch(`${api}?${parametros}`);
  const reservas = await lerResposta(resposta);
  $("#lista").innerHTML = reservas.map((r) => `<tr><td>${r.id}</td><td>${r.laboratorio}</td><td>${r.data_reserva}</td><td>${r.turno}</td><td>${r.responsavel}</td><td><button onclick='editar(${JSON.stringify(r)})'>Editar</button> <button onclick='excluirReserva(${r.id})'>Excluir</button></td></tr>`).join("");
  const resumo = await lerResposta(await fetch(`${api}/resumo`));
  $("#resumo").textContent = `Total: ${resumo.total} | manhã: ${resumo.por_turno.manha} | tarde: ${resumo.por_turno.tarde} | noite: ${resumo.por_turno.noite}`;
}

$("#form-reserva").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const id = $("#reserva-id").value;
  try {
    const resposta = await fetch(id ? `${api}/${id}` : api, { method: id ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(dadosDoFormulario()) });
    const reserva = await lerResposta(resposta);
    $("#mensagem").textContent = `Sucesso: reserva ${reserva.id} salva.`;
    cancelarEdicao();
    await listar();
  } catch (erro) { $("#mensagem").textContent = erro.message; }
});

window.editar = (reserva) => {
  $("#reserva-id").value = reserva.id; $("#laboratorio").value = reserva.laboratorio;
  $("#data-reserva").value = reserva.data_reserva; $("#turno").value = reserva.turno;
  $("#responsavel").value = reserva.responsavel; $("#quantidade").value = reserva.quantidade_pessoas;
  $("#finalidade").value = reserva.finalidade;
};

window.excluirReserva = async (id) => {
  try { await lerResposta(await fetch(`${api}/${id}`, { method: "DELETE" })); $("#mensagem").textContent = `Reserva ${id} excluída.`; await listar(); }
  catch (erro) { $("#mensagem").textContent = erro.message; }
};

function cancelarEdicao() { $("#form-reserva").reset(); $("#reserva-id").value = ""; }
$("#cancelar").addEventListener("click", cancelarEdicao);
$("#filtrar").addEventListener("click", listar);
$("#data-reserva").valueAsDate = new Date();
listar();
