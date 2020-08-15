import asyncio


class Test:

    async def hello_world(self):
        print("Hello World!")
        return "aaa"

    def __await__(self):
        a = self.hello_world().__await__()
        return a

async def main():
    test = await Test()
    print(test)

if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())



