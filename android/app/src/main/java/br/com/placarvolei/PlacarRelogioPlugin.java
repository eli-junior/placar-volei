package br.com.placarvolei;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.android.gms.wearable.DataClient;
import com.google.android.gms.wearable.MessageClient;
import com.google.android.gms.wearable.Node;
import com.google.android.gms.wearable.PutDataRequest;
import com.google.android.gms.wearable.Wearable;

import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.List;

/**
 * Ponte entre a quadra local (JS) e o relógio (CV7.TS3), pelo Wearable Data
 * Layer. O JS decide tudo; aqui só passam bytes:
 * <ul>
 *   <li>lance do relógio → evento {@code comando} {no, corpo};</li>
 *   <li>{@link #responder}: recibo e estado de volta ao relógio que enviou;</li>
 *   <li>{@link #publicarEstado}: o placar atual como DataItem, para o relógio
 *       ter o último estado mesmo ao reconectar.</li>
 * </ul>
 * O JS do WebView não roda confiável com a tela apagada (spike da TS3): lances
 * que chegam sem o plugin ativo esperam na fila e saem quando o JS volta; o
 * relógio reenvia o que não teve resposta.
 */
@CapacitorPlugin(name = "PlacarRelogio")
public class PlacarRelogioPlugin extends Plugin {
    static final String CAMINHO_ESTADO = "/placar/local/estado";
    static final String CAMINHO_COMANDO = "/placar/local/comando";
    static final String CAMINHO_RECIBO = "/placar/local/recibo";
    static final String CAMINHO_PING = "/placar/local/ping";
    private static final int MAX_ESPERANDO = 50;

    private static PlacarRelogioPlugin ativo;
    /** Lances que chegaram sem o JS ouvindo: {nó, corpo}. */
    private static final ArrayDeque<String[]> esperando = new ArrayDeque<>();

    /** Chamado pelo serviço do Data Layer, em thread própria. */
    static synchronized void entregar(String no, String corpo) {
        if (ativo != null) {
            ativo.emitir(no, corpo);
            return;
        }
        if (esperando.size() >= MAX_ESPERANDO) esperando.removeFirst();
        esperando.addLast(new String[] {no, corpo});
    }

    /** O relógio acabou de abrir e quer o estado agora; sem JS ouvindo, não há o que fazer. */
    static synchronized void pingar() {
        if (ativo != null) ativo.notifyListeners("ping", new JSObject());
    }

    private void emitir(String no, String corpo) {
        JSObject o = new JSObject();
        o.put("no", no);
        o.put("corpo", corpo);
        notifyListeners("comando", o, true);
    }

    @PluginMethod
    public void iniciar(PluginCall call) {
        synchronized (PlacarRelogioPlugin.class) {
            ativo = this;
            while (!esperando.isEmpty()) {
                String[] lance = esperando.removeFirst();
                emitir(lance[0], lance[1]);
            }
        }
        call.resolve();
    }

    @PluginMethod
    public void parar(PluginCall call) {
        synchronized (PlacarRelogioPlugin.class) {
            if (ativo == this) ativo = null;
        }
        call.resolve();
    }

    @Override
    protected void handleOnDestroy() {
        synchronized (PlacarRelogioPlugin.class) {
            if (ativo == this) ativo = null;
        }
    }

    @PluginMethod
    public void responder(PluginCall call) {
        String no = call.getString("no");
        String json = call.getString("json");
        if (no == null || json == null) {
            call.reject("no e json são obrigatórios");
            return;
        }
        MessageClient cliente = Wearable.getMessageClient(getContext());
        cliente.sendMessage(no, CAMINHO_RECIBO, json.getBytes(StandardCharsets.UTF_8))
            .addOnSuccessListener(id -> call.resolve())
            .addOnFailureListener(e -> call.reject("Relógio fora de alcance: " + e.getMessage()));
    }

    @PluginMethod
    public void publicarEstado(PluginCall call) {
        String json = call.getString("json");
        if (json == null) {
            call.reject("json é obrigatório");
            return;
        }
        DataClient cliente = Wearable.getDataClient(getContext());
        PutDataRequest pedido = PutDataRequest.create(CAMINHO_ESTADO);
        pedido.setData(json.getBytes(StandardCharsets.UTF_8));
        pedido.setUrgent();
        cliente.putDataItem(pedido)
            .addOnSuccessListener(item -> call.resolve())
            .addOnFailureListener(e -> call.reject("Não foi possível publicar o estado: " + e.getMessage()));
    }

    /** Relógios ao alcance, para a tela e o diagnóstico. */
    @PluginMethod
    public void nos(PluginCall call) {
        Wearable.getNodeClient(getContext()).getConnectedNodes()
            .addOnSuccessListener((List<Node> nos) -> {
                JSArray lista = new JSArray();
                for (Node n : nos) {
                    JSObject o = new JSObject();
                    o.put("id", n.getId());
                    o.put("nome", n.getDisplayName());
                    o.put("proximo", n.isNearby());
                    lista.put(o);
                }
                JSObject r = new JSObject();
                r.put("nos", lista);
                call.resolve(r);
            })
            .addOnFailureListener(e -> call.reject("Data Layer indisponível: " + e.getMessage()));
    }
}
