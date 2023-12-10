import asyncio
import websockets
import json

connected_clients = {}
game_state = {
    'roles': ['citizen', 'government', 'energy developer'],
    'budget': 1000000,
    'capacity_by_2035': 0,
    'capacity_by_2050': 0
}

async def game_server(websocket, path):
    role = await websocket.recv()
    connected_clients[websocket] = {'role': role, 'decision': None}
    
    try:
        async for message in websocket:
            data = json.loads(message)
            if 'decision' in data:
                connected_clients[websocket]['decision'] = data['decision']
            
            all_decided = all([client['decision'] for client in connected_clients.values()])
            if all_decided:
                total_capacity_2035 = sum([client['decision']['2035'] for client in connected_clients.values()])
                total_capacity_2050 = sum([client['decision']['2050'] for client in connected_clients.values()])
                
                if total_capacity_2035 <= game_state['budget'] and total_capacity_2050 <= game_state['budget']:
                    game_state['capacity_by_2035'] = total_capacity_2035
                    game_state['capacity_by_2050'] = total_capacity_2050
                    for client in connected_clients:
                        await client.send(json.dumps(game_state))
    except:
        pass
    finally:
        del connected_clients[websocket]

async def broadcast(message):
    # Send a message to all connected clients
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

start_server = websockets.serve(game_server, "localhost", 8767)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
