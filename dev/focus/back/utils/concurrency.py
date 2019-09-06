import asyncio
from concurrent.futures import ThreadPoolExecutor
# import shelve
from typing import Any, Awaitable, Callable, Tuple

# from . import ROUTINES_FILE


# def asyncinit(cls):
#     """Преобразовать синхронный класс в асинхронный.

#     Параметры:
#       :param cls: — декорируемый класс.

#     Вернуть асинхронный класс.
#     """

#     __new__ = cls.__new__

#     async def init(obj, *args, **kwargs):
#         await obj.__init__(*args, **kwargs)
#         return obj

#     def new(cls, *args, **kwargs):
#         obj = __new__(cls, *args, **kwargs)
#         coro = init(obj, *args, **kwargs)
#         coro.__init__ = lambda *_1, **_2: None

#         return coro

#     cls.__new__ = new

#     return cls

async def add_coroutines(*coroutines: Awaitable) -> None:
    return await asyncio.gather(*coroutines)


async def sleep_for(sec: int) -> None:
    await asyncio.sleep(sec)
    print('Hi')


class CoroWorker:
    """Обработчик асинхронных команд.

    Методы:
      :meth __init__(self): — конструктор экземпляров класса;
      :meth run(self, *coros): — дождаться выполнения сопрограмм и вернуть
    результат их выполнения;
      :async meth dispatch(self, *coros): — """

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    async def dispatch(self, *coros: Awaitable[Any]) -> Awaitable:
        return await asyncio.gather(*coros)

    def run(self, *coros: Awaitable[Any]) -> Any:
        return self.loop.run(self.dispatch(*coros))

    def run_forever(self, *coros: Awaitable[Any]) -> Any:
        return self.loop.run_forever(self.dispatch(*coros))

    async def sync_to_async(
            self, *coros: Tuple[Awaitable, Any], max_workers=3) -> Any:
        executor = ThreadPoolExecutor(max_workers=max_workers)
        results = []

        for coro in coros:
            res = await self.loop.run_in_executor(executor, coro, *args)
            results.append(res)

        return results


# def run(coroutine):
#     return asyncio.run(coroutine)


# async def main():
#     with shelve.open(ROUTINES_FILE) as db:
#         async for routine in db:
#             await worker()
