// ==============================================================================
// Builds a viewer Game object from a saved game (the JSON written by
// run_one_game(..., save_file=...)). Adapted from loadGameFromDisk() in the
// diplomacy web interface (gui/utils/load_game_from_disk.js), GNU AGPL v3.
// ==============================================================================
import {STRINGS} from "../../diplomacy/utils/strings";
import {Game} from "../../diplomacy/engine/game";

export function gameFromSavedData(savedData) {
    const gameObject = {};
    gameObject.game_id = `(local) ${savedData.id}`;
    gameObject.map_name = savedData.map;
    gameObject.rules = savedData.rules;
    gameObject.state_history = {};
    gameObject.message_history = {};
    gameObject.order_history = {};
    gameObject.result_history = {};

    // Load all saved phases (expect the latest one) to history fields.
    for (let i = 0; i < savedData.phases.length - 1; ++i) {
        const savedPhase = savedData.phases[i];
        const gameState = savedPhase.state;
        const phaseOrders = savedPhase.orders || {};
        const phaseResults = savedPhase.results || {};
        const phaseMessages = {};
        if (savedPhase.messages) {
            for (let message of savedPhase.messages) {
                phaseMessages[message.time_sent] = message;
            }
        }
        if (!gameState.name)
            gameState.name = savedPhase.name;
        gameObject.state_history[gameState.name] = gameState;
        gameObject.message_history[gameState.name] = phaseMessages;
        gameObject.order_history[gameState.name] = phaseOrders;
        gameObject.result_history[gameState.name] = phaseResults;
    }

    // Load latest phase separately and use it later to define the current game phase.
    const latestPhase = savedData.phases[savedData.phases.length - 1];
    const latestGameState = latestPhase.state;
    const latestPhaseOrders = latestPhase.orders || {};
    const latestPhaseResults = latestPhase.results || {};
    const latestPhaseMessages = {};
    if (latestPhase.messages) {
        for (let message of latestPhase.messages) {
            latestPhaseMessages[message.time_sent] = message;
        }
    }
    if (!latestGameState.name)
        latestGameState.name = latestPhase.name;
    // TODO: NB: What if latest phase in loaded JSON contains order results? Not sure if it is well handled.
    gameObject.result_history[latestGameState.name] = latestPhaseResults;

    gameObject.messages = [];
    gameObject.role = STRINGS.OBSERVER_TYPE;
    gameObject.status = STRINGS.COMPLETED;
    gameObject.timestamp_created = 0;
    gameObject.deadline = 0;
    gameObject.n_controls = 0;
    gameObject.registration_password = '';
    const game = new Game(gameObject);

    // Set game current phase and state using latest phase found in JSON file.
    game.setPhaseData({
        name: latestGameState.name,
        state: latestGameState,
        orders: latestPhaseOrders,
        messages: latestPhaseMessages
    });
    return game;
}
