class GestureRecognizer:
    def recognize(self, lm: list) -> str | None:
        if not lm or len(lm) < 21:
            return None

        # Finger extension: tip y < pip y means finger is UP
        def ext(tip, pip):
            return lm[tip]["y"] < lm[pip]["y"]

        i = ext(8,  6)   # index
        m = ext(12, 10)  # middle
        r = ext(16, 14)  # ring
        p = ext(20, 18)  # pinky
        up = sum([i, m, r, p])

        W  = lm[0]   # wrist
        T  = lm[4]   # thumb tip
        TI = lm[3]   # thumb IP (joint before tip)

        
        thumb_out = T["x"] > TI["x"] + 0.03

        # ── PRIORITY ORDER — upar se neeche check hota hai ──────────────

        # 1. THUMBS UP — sabse pehle: up==0, thumb clearly OOPAR wrist se
        if up == 0 and T["y"] < W["y"] - 0.06:
            return "THUMBS_UP"

        # 2. THUMBS DOWN — up==0, thumb clearly NEECHE wrist se
        if up == 0 and T["y"] > W["y"] + 0.06:
            return "THUMBS_DOWN"

        # 3. FIST — up==0, thumb bhi andar (thumb_out False)
        if up == 0 and not thumb_out:
            return "FIST"

        # 4. PINCH — thumb + index close, baaki curl (thoda loosened: 0.09)
        dx = abs(T["x"] - lm[8]["x"])
        dy = abs(T["y"] - lm[8]["y"])
        if dx < 0.09 and dy < 0.09 and not m and not r:
            return "PINCH"

        # 5. POINTING — sirf index
        if i and not m and not r and not p:
            return "POINTING"

        # 6. TWO FINGERS — index + middle
        if i and m and not r and not p:
            return "TWO_FINGERS"

        # 7. THREE FINGERS — index + middle + ring
        if i and m and r and not p:
            return "THREE_FINGERS"

        # 8. FOUR FINGERS — chaaron (thumb nahi)
        if i and m and r and p:
            return "FOUR_FINGERS"

        # 9. ROCK — index + pinky (horns gesture)
        if i and not m and not r and p:
            return "ROCK"

        # 10. OPEN HAND — chaaron + thumb bahar
        if up == 4 and thumb_out:
            return "OPEN_HAND"

        return None