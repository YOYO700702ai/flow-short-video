# 05 Flow 提示詞｜<片名>｜段 01

> AI 寫，一鏡一段英文提示詞，使用者貼進 Flow。
> 設定（每一鏡都一樣，除了長度）：**影片、影格、16:9、Omni 1.2 Flash、360p、長度照下表、x1**。
> 輸入框下面會顯示「生成內容會使用 N 點」，送出前看一眼：360p 每秒 1 點，綁角色、@ 語音都不另外扣點。
>
> **每一鏡怎麼貼**：
> 1. 放第一格：上傳後**等清單出現檔名再選**；送出前看一眼縮圖是不是這一鏡的（放錯點縮圖移除再加）。
> 2. 表上「@」欄有寫的鏡：在空的輸入框打「@」→ **先看清單左邊的分類**（會停在上次用的）：角色：切到「角色」→ 選角色 →「新增至提示詞」；旁白：切到「語音」→ 搜尋聲音名 → 點一下就直接插進去。
> 3. 按 End 移到最後，貼上「【先插入 @…】」**後面**那段（開頭留一個空格）。標籤要用 @ 選，打字打出來的沒有用。
> 4. 「@」欄寫「不用 @」的鏡，整段直接貼。

## 寫法規則（每一段都要照）

0. **要固定聲音的鏡，最前面是 @ 標籤**：
   - 角色講話：`【先插入 @大哥】 is the fat little pig in this shot; he speaks with his own voice.`
     畫面裡還有別人：再加 `Only the fat little pig speaks; the others' mouths stay closed.`
   - 旁白：`【先插入 @語音 Vindemiatrix】 is the voice of the off-screen storyteller; no character on screen speaks.`
   - 沒台詞的鏡不用 @。角色要從畫面外進來、第一格看不到他時，才 @ 他只為了長相：`【先插入 @大哥】 is the fat little pig; he appears in this shot and does not speak.`
   - 一鏡只讓一個角色講話。
1. **開頭兩句固定**：`Starting from the attached image. In a single continuous shot, no scene cuts.`
   不寫第二句，Flow 會自己剪成好幾個鏡頭。有 @ 的鏡，接在 @ 那句後面。
2. **鏡頭寫可以檢查的條件**，不要只寫「鏡頭不動」：
   `The camera stays fixed; the cottage and the three little pigs stay the same size and in the same place in every frame.`
3. **畫風一句**（照第 1 關定的畫風寫，每一鏡同一句）：例如三隻小豬是 `A warm hand-painted storybook cartoon, the same style as the image.`
4. **只寫會變的部分**：第一格已經畫好了，不要重新描述圖；也不要寫跟圖相反的景別（圖是特寫就不要寫 wide shot）。
5. **每鏡 2～3 拍，用時間分段**：`[0-2s] … [2-4s] … [4-6s] …`；4 秒最多 2 拍，6 秒最多 3 拍。動作用正常速度。
6. **多個角色要寫誰先誰後、動作不一樣**，並加：`Their timing and head angles are different from each other at every moment.`
7. **★每一個會出聲的地方都寫語言和中文原文★**：
   - 旁白：`From the first second, the storyteller narrates off-screen in Mandarin Chinese, warm and gentle: 從前，豬媽媽有三隻小豬。`
   - 角色講話：`She speaks in Mandarin Chinese, gentle and encouraging, her mouth clearly moving with each syllable: 孩子們長大了，去蓋自己的房子吧！`
   - 喊一聲也要寫：`The three little pigs call back from far away in Mandarin Chinese: 媽媽再見！`
   - **只寫英文的 "calling goodbye"，Flow 就會讓角色講英文。**
   - 不要人聲：`No voices.`；只要寫出來的那句：加 `No other voices.`
   - 講話之前嘴要閉著：`Her mouth stays closed until she speaks.`；不講話的人：`All their mouths stay closed.`
8. **指方向要寫指向什麼東西**（建議做法）：寫 `points toward the path behind the three pigs`，不要只寫 `points to the right`

9. **結尾固定三句**：`Sound design: <具體的聲音>. No music. No subtitles. No on-screen text.`
10. 要接下一鏡的，可以加：`… and holds still for the last half second.`
11. **火、燈、門這類東西照分鏡表寫死狀態**：`The fireplace stays cold and unlit, no fire at all.`；Sound design 也不要寫會讓它改變狀態的聲音（壁爐沒火就不要寫 crackle）。（建議做法，生成後要特別看）

## 每一鏡

「第一格」欄寫**實際送進 Flow 的那個檔**（有 _v2、_v3 就寫那一版），事後才分得出用的是哪張。

| 鏡 | 第一格（用哪一個檔） | @ | 長度 | 點數 |
|---|---|---|---|---|
| 1 | 第一格_送進Flow/K1.png | @語音 <旁白聲音>（旁白） | 6 秒 | 6 |
| 2 | 第一格_送進Flow/K2_v2.png | @<角色> | 6 秒 | 6 |
| 3 | 第一格_送進Flow/K3.png | 不用 @（沒人講話） | 4 秒 | 4 |
| 4 | 第一格_送進Flow/K4.png | @<角色> | 6 秒 | 6 |
| 5 | 第一格_送進Flow/K5.png | 不用 @（沒人講話） | 4 秒 | 4 |
| 6 | 第一格_送進Flow/K6.png | @<角色> | 6 秒 | 6 |

驗收時用：有台詞（含旁白）的鏡＝`--有台詞 S1,S2,S4`（照上表填）。

### 鏡 1（6 秒，旁白）

```
【先插入 @語音 <旁白聲音>】 is the voice of the off-screen storyteller; no character on screen speaks. Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed; <哪些東西> stay the same size and in the same place in every frame. <畫風一句>, the same style as the image. [0-2s] <第一拍>. [2-4s] <第二拍>. [4-6s] <第三拍>. From the first second, the storyteller narrates off-screen in Mandarin Chinese, <語氣>: <中文原文> <畫面裡的人> do not speak; their mouths stay closed. Sound design: <聲音>. No music. No subtitles. No on-screen text.
```

### 鏡 2（6 秒，@<角色> 講話）

```
【先插入 @<角色>】 is <這一鏡裡是哪一個> in this shot; he speaks with his own voice. Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed; <哪些東西> stay the same size and in the same place in every frame. <畫風一句>, the same style as the image. [0-2s] <第一拍>. [2-4s] <he says in Mandarin Chinese, 語氣, his mouth clearly moving with each syllable: 中文原文> [4-6s] <第三拍>. Only <講話的人> speaks; the others' mouths stay closed. Sound design: <聲音>. No other voices. No music. No subtitles. No on-screen text.
```

### 鏡 3（4 秒，沒人講話，不用 @）

```
Starting from the attached image. In a single continuous shot, no scene cuts. The camera stays fixed; <哪些東西> stay the same size and in the same place in every frame. <畫風一句>, the same style as the image. [0-2s] <第一拍>. [2-4s] <第二拍>. All their mouths stay closed. Sound design: <聲音>. No voices. No music. No subtitles. No on-screen text.
```
