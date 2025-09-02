## Pythonで学ぶ債券・金利デリバティブ *(QuantLib-Python 入門)*

### 正誤表

| ページ | 誤 | 正 |
|--------|----|----|
| 74 | P({X ≤ −50) | P({X ≤ −50}) |

---

### 追記

#### 9.3.1節 早期終了
- 例えばp.176のコード例  
  ```python
  es = EarlyStopping(monitor='loss', patience=30)
