# Flow 提示詞怎麼寫

範本：`assets/templates/05_Flow提示詞.md`。下面有兩組實際送出、結果正確的提示詞：綁聲音的大哥兩鏡、旁白和多人同框的兩鏡。
三隻小豬段 03～06 全部 24 鏡的提示詞在 `examples/three-little-pigs/05_Flow提示詞_段03-06.md`。

## 設定（每一鏡都一樣，只有長度不同）

影片、**影格**（第一格用你畫的圖）、16:9、**Omni 1.2 Flash**、**360p**、長度、**x1**。
360p 每秒 1 點；有台詞的鏡 6 秒、其他 4～5 秒（比分鏡多 1～2 秒，留給剪接）。用 @ 綁角色聲音、@ 旁白語音都不另外扣點。

## 規則

0. **要固定聲音的鏡，最前面先放 @ 標籤**（使用者在 Flow 打「@」從清單選，畫面上顯示成 `[大哥]`，**不是打字**；後面那句照貼）：
   - **角色講話**：`【先插入 @大哥】 is the fat little pig in this shot; he speaks with his own voice.`
     「is … in this shot」寫清楚這一鏡裡是哪一個（胖的、戴草帽的…），尤其畫面裡有好幾個角色時。
   - **畫面裡還有別人**：照樣只 @ 講話的那一個，提示詞裡再加 `Only the fat little pig speaks; the others' mouths stay closed.`
   - **旁白**：不用建角色，直接 @ 一個預設聲音：`【先插入 @語音 Vindemiatrix】 is the voice of the off-screen storyteller; no character on screen speaks.`
     旁白那句寫 `From the first second, the storyteller narrates off-screen in Mandarin Chinese, warm and gentle: 原文`，再加 `The pigs do not speak; their mouths stay closed.`
   - **@ 只給這一鏡會講話的角色。** 沒台詞的鏡不用 @，長相靠第一格就穩得住。
     角色要從畫面外進來、第一格裡看不到他時，才 @ 他只為了長相：`is the fat little pig; he appears in this shot and does not speak.`
   - **一鏡只讓一個角色講話**；兩人對話拆成兩鏡。
1. **開頭兩句固定**：`Starting from the attached image. In a single continuous shot, no scene cuts.`
   不寫第二句，Flow 會自己剪成好幾個鏡頭。有 @ 的鏡，這兩句接在 @ 那句後面。
2. **鏡頭寫可以檢查的條件**：`The camera stays fixed; the cottage and the three little pigs stay the same size and in the same place in every frame.`
   不要只寫 "camera is locked off"，也不要寫一串否定句（"no push in, no zoom…"），那樣反而會讓鏡頭動。
3. **畫風一句**（照第 1 關定的畫風寫，每一鏡同一句）：例如三隻小豬是 `A warm hand-painted storybook cartoon, the same style as the image.`
4. **只寫會變的部分**：第一格已經畫好了，不要重新描述圖；也**不要寫和圖相反的景別**（圖是特寫就不要寫 wide shot），不然它會改構圖。
5. **每鏡 2～3 拍，用時間分段**：`[0-2s] … [2-4s] … [4-6s] …`。4 秒最多 2 拍、6 秒最多 3 拍。動作用正常速度，不寫 slow motion。
6. **多個角色寫誰先誰後、動作不一樣**，加：`Their timing and head angles are different from each other at every moment.`
7. **★每一個會出聲的地方都寫語言和中文原文★**（只寫英文描述，例如 "calling goodbye"，Flow 就會讓角色講英文）
   - 旁白：`From the first second, the storyteller narrates off-screen in Mandarin Chinese, warm and gentle: 從前，豬媽媽有三隻小豬。`
   - 講話：`She speaks in Mandarin Chinese, gentle and encouraging, her mouth clearly moving with each syllable: 孩子們長大了，去蓋自己的房子吧！`
   - 喊一聲也要寫：`The three little pigs call back from far away in Mandarin Chinese: 媽媽再見！`
   - 只要那一句：加 `No other voices.`；完全不要人聲：`No voices.`
   - 講話前嘴閉著：`Her mouth stays closed until she speaks.`；不講話的人：`All their mouths stay closed.`
   - 中文寫在冒號後面、不加引號（加引號有時會變成畫面上的字幕）。
8. **指方向要寫指向什麼東西**（建議做法）：`points toward the path behind the three little pigs`，不要寫畫面的方向（toward the right of the frame）。
9. **動作要寫得具體、可以量**（建議做法）：寫 `walks four steps out of the doorway onto the path`，不要只寫 "steps out of the door"。
10. **結尾固定**：`Sound design: <具體的聲音>. No music. No subtitles. No on-screen text.`
11. 要接下一鏡的，可以加 `… and holds still for the last half second.`
12. 一兩秒的空鏡不要寫突發事件（掉落、滾動），只寫從第一格就一直在動的東西（風吹草、雲、水）。
13. **之後才會改變狀態的東西，寫死現在的狀態**（火、燈、門、窗）：`The fireplace stays cold and unlit, no fire at all.`；Sound design 也不要寫會讓它改變狀態的聲音（壁爐沒火就不要寫 crackle）。（建議做法，生成後要特別看）

## 範本

有角色講話的鏡（使用者先用 @ 插入角色，再貼「【先插入 @角色】」後面那段）：

```
【先插入 @<角色>】 is <這一鏡裡是哪一個> in this shot; he speaks with his own voice. Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed; <哪些東西> stay the same size and in the same place in every frame. <畫風一句>, the same style as the image. [0-2s] <第一拍>. [2-4s] <第二拍：he says in Mandarin Chinese, <語氣>, his mouth clearly moving with each syllable: <中文原文>> [4-6s] <第三拍>. Only <講話的人> speaks; the others' mouths stay closed. Sound design: <具體的聲音>. No other voices. No music. No subtitles. No on-screen text.
```

（畫面裡只有講話的人時，`Only … stay closed.` 那句可以拿掉。）

旁白的鏡（使用者先用 @ 從「語音」分類選旁白的聲音，再貼後面那段）：

```
【先插入 @語音 <旁白的聲音>】 is the voice of the off-screen storyteller; no character on screen speaks. Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed; <哪些東西> stay the same size and in the same place in every frame. <畫風一句>, the same style as the image. [0-2s] <第一拍：誰做什麼>. [2-4s] <第二拍>. [4-6s] <第三拍>. From the first second, the storyteller narrates off-screen in Mandarin Chinese, warm and gentle: <中文原文> <畫面裡的人> do not speak; their mouths stay closed. Sound design: <具體的聲音>. No music. No subtitles. No on-screen text.
```

沒有人出聲的鏡（不用 @，整段貼上）：

```
Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed; <哪些東西> stay the same size and in the same place in every frame. <畫風一句>, the same style as the image. [0-2s] <第一拍：誰做什麼>. [2-4s] <第二拍>. [4-6s] <第三拍>. <畫面裡的人> mouths stay closed. Sound design: <具體的聲音>. No voices. No music. No subtitles. No on-screen text.
```

## 範例一：綁聲音的兩鏡（三隻小豬段 02，大哥＝Fenrir）

設定：影格模式、Omni 1.2 Flash、360p、6 秒、x1，兩鏡共 12 點（綁角色不另外扣點）。最前面的 `[大哥]` 是用 @ 插入的角色標籤。
結果：兩鏡構圖都從第一格開始；台詞中文（98.9%、99.7%）；使用者聽了確認兩鏡是同一個聲音。

鏡 2（台詞在 2.72～4.70 秒）：

```
[大哥] is the fat little pig in this shot; he speaks with his own voice. Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed; the pig and the hut stay the same size and in the same place in every frame. A warm hand-painted storybook cartoon, the same style as the image. [0-1s] The fat little pig pats the straw wall proudly with his raised hoof. [1-2s] The whole hut wobbles and a few straws drop from the roof. [2-4s] He shrugs and says in Mandarin Chinese, lazy and pleased, his mouth clearly moving with each syllable: 好啦，夠住就好！ [4-5s] He grins with his mouth closed. Sound design: straw rustling, a creak as the hut wobbles. No other voices. No music. No subtitles. No on-screen text.
```

鏡 6（台詞在 1.80～3.74 秒）：

```
[大哥] is the fat little pig in this shot; he speaks with his own voice. Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed inside the straw hut; the pig and the straw bed stay the same size and in the same place in every frame. A warm hand-painted storybook cartoon, the same style as the image. [0-1s] The fat little pig sleeps with the straw hat over his face. [1-2s] He jolts awake: the hat slides off and he sits bolt upright, his eyes wide and round. [2-4s] He clutches his hat to his chest and shouts in Mandarin Chinese, scared, his mouth clearly moving with each syllable: 不行不行！ [4-6s] From outside comes a very long, deep breath in; the straw walls begin to tremble and a few straws drift down. Sound design: a long deep inhale from outside, trembling straw. No other voices. No music. No subtitles. No on-screen text.
```

## 範例二：旁白和多人同框（三隻小豬段 03，旁白＝Vindemiatrix、二哥＝Puck）

鏡 4（6 秒，旁白）：使用者打「@」→ 清單左邊選「語音」→ 搜尋 Vindemiatrix → 點一下，標籤就插進提示詞。結果：旁白中文、一字不差，小豬都沒開口。

```
[Vindemiatrix] is the voice of the off-screen storyteller; no character on screen speaks. Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed; the wooden house stays the same size and in the same place in every frame. A warm hand-painted storybook cartoon, the same style as the image. [0-2s] The little pig in the blue cap hammers a nail into the wooden wall, tap, tap. [2-4s] He hears footsteps and turns his head to the left; the fat little pig in the straw hat comes running along the path from the left. [4-6s] The pig in the blue cap lowers his hammer and looks at his brother in surprise. From the first second, the storyteller narrates off-screen in Mandarin Chinese, warm and gentle: 大哥一路跑到二哥的木頭屋。 The pigs do not speak; their mouths stay closed. Sound design: hammer taps, running footsteps, birds. No music. No subtitles. No on-screen text.
```

鏡 5（5 秒，兩隻豬同框、只有二哥講話）：只 @ 二哥。結果：只有二哥開口。

```
[二哥] is the little pig in the blue cap in this shot; he speaks with his own voice. Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed; the door and the pigs stay the same size and in the same place in every frame. A warm hand-painted storybook cartoon, the same style as the image. [0-1s] The pig in the blue cap holds the door open and waves his hoof. [1-3s] He calls in Mandarin Chinese, urgent, his mouth clearly moving with each syllable: 快進來！ [3-5s] The fat little pig in the straw hat runs in through the door. Only the pig in the blue cap speaks; the other pig's mouth stays closed. Sound design: running footsteps, the wooden door creaking. No other voices. No music. No subtitles. No on-screen text.
```

> 打 @ 之後先看清單左邊停在哪個分類：旁白在「語音」、角色在「角色」。
