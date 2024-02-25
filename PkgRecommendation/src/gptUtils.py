import os

os.environ["OPENAI_API_KEY"] = "sk-YmqNIKPfCAGzR36F6Ku54dMd3Xz5xFHBS33Wep6BQdQof58p"

import openai


class GPTClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key="sk-YmqNIKPfCAGzR36F6Ku54dMd3Xz5xFHBS33Wep6BQdQof58p",
            base_url="https://api.chatanywhere.tech/v1"
        )

    def getResponse(self, updateFreq, openCount, closeCount, lastCommitTime):
        description = "请用中文回答我的以下问题：我有一个python第三方包，"
        description = description + "它的版本更新频率是" + str(updateFreq) + "天，"
        description = description + "它的github库中close的issue为" + str(
            closeCount) + "，open的issue为" + str(openCount) + "，"
        description = description + "它的最后一次commit时间为" + lastCommitTime.strftime("%Y-%m-%d %H:%M:%S")

        try:
            print(description)
            gptDescription = ""

            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个了解python第三方包功能的助手"},
                    {"role": "user",
                     "content": f"{description},请从更新频率，解决问题的可能性，维护程度，该包的流行程度这4个方面，定性地描述这个包。"},
                ]
            )

            gptDescription = completion.choices[0].message.content
        except Exception as err:
            return {
                "message": "error",
                "status": 500,
                "data": err
            }
        return {
            "message": "Request processed successfully",
            "status": 200,
            "data": gptDescription
        }


if __name__ == "__main__":
    gptClient = GPTClient()
