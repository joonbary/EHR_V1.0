"""
WebSocket 서버 - UI/UX 업그레이드 진행상황 브로드캐스팅
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketServer:
    """진행상황 브로드캐스팅 WebSocket 서버"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.task_history = []
    
    async def register_client(self, websocket):
        """클라이언트 등록"""
        self.clients.add(websocket)
        logger.info(f"새 클라이언트 연결: {websocket.remote_address}")
        
        # 연결 확인 메시지 전송
        await websocket.send(json.dumps({
            'type': 'welcome',
            'message': 'WebSocket 서버에 연결되었습니다',
            'timestamp': datetime.now().isoformat(),
            'history_count': len(self.task_history)
        }, ensure_ascii=False))
        
        # 기존 히스토리 전송
        if self.task_history:
            await websocket.send(json.dumps({
                'type': 'history',
                'data': self.task_history[-10:]  # 최근 10개만
            }, ensure_ascii=False))
    
    async def unregister_client(self, websocket):
        """클라이언트 등록 해제"""
        if websocket in self.clients:
            self.clients.remove(websocket)
            logger.info(f"클라이언트 연결 해제: {websocket.remote_address}")
    
    async def broadcast_message(self, message: dict):
        """모든 클라이언트에 메시지 브로드캐스트"""
        if self.clients:
            # 히스토리에 저장
            self.task_history.append(message)
            
            # 연결이 끊긴 클라이언트 제거
            disconnected = set()
            
            # 모든 클라이언트에 전송
            for websocket in self.clients:
                try:
                    await websocket.send(json.dumps(message, ensure_ascii=False))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(websocket)
                except Exception as e:
                    logger.error(f"메시지 전송 실패: {e}")
                    disconnected.add(websocket)
            
            # 연결 끊긴 클라이언트 제거
            for websocket in disconnected:
                await self.unregister_client(websocket)
    
    async def handle_client(self, websocket, path):
        """클라이언트 핸들러"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"받은 메시지: {data.get('type', 'unknown')}")
                    
                    # 받은 메시지를 모든 클라이언트에 브로드캐스트
                    await self.broadcast_message(data)
                    
                except json.JSONDecodeError:
                    logger.error(f"잘못된 JSON 형식: {message}")
                except Exception as e:
                    logger.error(f"메시지 처리 오류: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def start(self):
        """서버 시작"""
        logger.info(f"WebSocket 서버 시작: ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # 무한 실행


def main():
    """메인 실행 함수"""
    server = WebSocketServer()
    asyncio.run(server.start())


if __name__ == "__main__":
    main()