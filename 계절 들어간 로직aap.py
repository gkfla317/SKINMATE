def get_morning_routine_structure(db, skin_type, concerns, current_season, makeup='no'):
    """5가지 피부 타입과 주요 고민에 따른 아침 루틴을 구조화하여 추천합니다."""
    steps = []
    user_concerns = {c['name'] for c in concerns if c.get('name')}
    
    # ------------------- 공통 로직 -------------------
    step2_query, step2_params, step2_desc = None, [], ""
    has_moisture_concern = '수분' in user_concerns
    has_wrinkle_elasticity_moisture_concern = '주름' in user_concerns or '탄력' in user_concerns and '수분' in user_concerns

    # 계절 -> 피부 고민 : 주름,탄력 (o/x) -> 피부 타입            바꾸기!!!!! 간단하게 보여주기 식으로 만들면 됨.
    # ------------------- 여름 -------------------  
    if current_season == 'summer': 
        # 고민 : 계절 -> 주름,탄력 ox -> 피부타입
        if has_wrinkle_elasticity_moisture_concern: 
            # ------------------- 💧 건성 (Dry) -------------------
            if skin_type == 'Dry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%젤%' OR name LIKE '%워터%' OR name LIKE '%크림%') 
                    AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%약산성%' OR name LIKE '%스쿠알란%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "피부 장벽을 보호하고 수분을 유지해주는 클렌징 제품을 사용하세요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%레티놀%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "안티에이징 제품으로 주름과 탄력을 관리하고, 피부에 촉촉한 수분감을 더하세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%판테놀%' OR name LIKE '%고보습%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "산뜻한 안티에이징으로 하루를 시작하고, 빈틈없이 촉촉한 피부를 느껴보세요.", "primary_recommendation": p3, "alternatives": a3}) 

            # ------------------- ✨ 지성 (Oily) -------------------
            if skin_type == 'Oily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%') 
                    AND (name LIKE '%티트리%' OR name LIKE '%그린%' OR name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "피부에 자극을 주지 않으면서도 수분을 남겨주는 젤 타입이나 약산성 클렌저를 사용해 보세요.<br>과도한 세안은 오히려 피부를 건조하게 만들어 유분 분비를 촉진할 수 있습니다.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('안티에이징', '수분', '모공')                
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%나이아신%' OR name LIKE '%나이아신%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%저분자%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "세안 후에는 끈적임 없이 가볍게 흡수되는 주름, 탄력 관리 제품으로 유수분 밸런스를 맞춰주세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%수분 크림%' OR name LIKE '%젤%' OR name LIKE '%워터 크림%' OR name LIKE '%로션%')
                    AND (name LIKE '%세라마이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "가벼운 사용감으로 피부 속까지 촉촉하게 채워요.", "primary_recommendation": p3, "alternatives": a3}) 
                    
            # ------------------- ⚖️ 중성 (Normal) -------------------
            if skin_type == 'Normal':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '기본')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "유수분 밸런스가 깨지지 않도록 가볍게 물세안 또는 순한 클렌저 사용을 추천드립니다.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category In ('스킨/토너') 
                    AND sub_category IN ('수분', '안티에이징', '리페어')  
                    AND (name LIKE '%나이아신%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%' OR name LIKE '%히알루론산%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "즉각적인 탄력과 수분 충전을 느껴보세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%히알루론산%' OR name LIKE '%항%' OR name LIKE '%스쿠알란%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "가볍게 수분 장벽을 지키고 탄력있는 피부를 가꿔요.", "primary_recommendation": p3, "alternatives": a3}) 
            # ------------------- 복합 건성 (CombinationDry) -------------------
            if skin_type == 'CombinationDry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%' OR name LIKE '%히알루론산%' OR name LIKE '%수분%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "촉촉함은 남기면서 노폐물만 깨끗하게 씻어내는 것이 중요합니다.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category In ('스킨/토너', '에센스/앰플/세럼') 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')  
                    AND (name LIKE '%병풀%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "세안 후에는 끈적임 없이 가볍게 흡수되는 안티에이징 제품으로 유수분 밸런스를 맞춰주세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "유분이 많은 T존은 가볍게, 건조한 U존은 얇게 덧발라주세요.", "primary_recommendation": p3, "alternatives": a3}) 
               
            # ------------------- 복합 지성 (CombinationOily) -------------------
            if skin_type == 'CombinationOily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%' OR name LIKE '%저자극%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "T존은 산뜻하게, U존은 촉촉하게", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '스킨/토너' 
                    AND sub_category IN ('안티에이징', '모공', '수분')  
                    AND (name LIKE '%병풀%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "세안 후에는 끈적임 없이 가볍게 흡수되는 안티에이징 제품으로 유수분 밸런스를 맞춰주세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '모공', '수분')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%로션%' OR  name LIKE '%젤%')
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%라이트%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "유분이 많은 T존은 가볍게, 건조한 U존은 얇게 덧발라주세요.", "primary_recommendation": p3, "alternatives": a3}) 
        
        # 고민 : 수분 -> 피부 타입과 연관ㅇ
        elif has_moisture_concern: 
            # ------------------- 💧 건성 (Dry) -------------------
            if skin_type == 'Dry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%젤%' OR name LIKE '%워터%' OR name LIKE '%크림%') 
                    AND name LIKE '%약산성%'
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "악산성 제품을 사용해 피부에 자극을 줄여요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category In ('스킨/토너', '에센스/앰플/세럼')
                    AND sub_category IN ('수분', '보습', '기본')
                    AND (name LIKE "%스킨%" OR name LIKE "%토너%" OR name LIKE '%세럼%')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%나이아신%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "즉각적인 수분 보충으로 피부를 케어해요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('수분', '보습', '기본')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%세라마이드%' OR name LIKE '%스쿠알란%' OR name LIKE '%히알루론산%' OR name LIKE '%고보습%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "산뜻한 안티에이징으로 하루를 시작하고, 빈틈없이 촉촉한 피부를 느껴보세요.", "primary_recommendation": p3, "alternatives": a3}) 

            # ------------------- ✨ 지성 (Oily) -------------------
            if skin_type == 'Oily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '기본', '보습') 
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%') 
                    AND (name LIKE '%티트리%' OR name LIKE '%그린%' OR name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "과도한 세안은 오히려 피부를 건조하게 만들어 유분 분비를 촉진할 수 있어요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '스킨/토너' 
                    AND sub_category IN ('수분', '기본', '보습')                
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%그린%' OR name LIKE '%녹차%' OR name LIKE '%히알루론산%' OR name LIKE '%병풀%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "가벼운 사용감의 제품을 사용하세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%수분 크림%' OR name LIKE '%젤%' OR name LIKE '%워터 크림%' OR name LIKE '%로션%')
                    AND (name LIKE '%녹차%' OR name LIKE '%병풀%' OR name LIKE '%나이아신%' OR name LIKE '%그린%'  OR name LIKE '%알로에%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "리치하지 않은 사용감으로 촉촉하지만 산뜻한 피부를 느껴봐요.", "primary_recommendation": p3, "alternatives": a3}) 
                    
            # ------------------- ⚖️ 중성 (Normal) -------------------
            if skin_type == 'Normal':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '기본',' '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "유수분 밸런스가 깨지지 않도록 가볍게 물세안 또는 순한 클렌저 사용을 추천드려요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '스킨케어'
                    AND middle_category = '스킨/토너'
                    AND sub_category IN ('수분', '기본',' '보습')  
                    AND (name LIKE '%저분자%' OR name LIKE '%병풀%' OR name LIKE '%히알루론산%' OR name LIKE '%녹차%'OR name LIKE '%그린%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "즉각적인 탄력과 수분 충전을 느껴보세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '스킨케어'
                    AND middle_category = '크림'
                    AND sub_category IN ('수분', '기본',' '보습')   
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%펩타이드%' OR name LIKE '%나이아신%' OR name LIKE '%히알루론산%' OR name LIKE '%항%' OR name LIKE '%병풀%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "유수분 밸런스를 지키며 지금의 피부상태를 유지해요.", "primary_recommendation": p3, "alternatives": a3}) 
           
           
            # ------------------- 복합 건성 (CombinationDry) -------------------
            if skin_type == 'CombinationDry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '보습')   
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%' OR name LIKE '%히알루론산%' OR name LIKE '%수분%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "자면서 나온 노폐물만 가볍게 씻어내요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '에센스/앰플/세럼')
                    AND sub_category IN ('수분', '보습')  
                    AND (name LIKE '%병풀%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "내 피부에 부족한 수분을 채워줘요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('수분', '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "피지 분비가 활발한 T존에는 산뜻하게, 건조한 U존에는 적은 양을 덧발라 촉촉함을 유지하세요.", "primary_recommendation": p3, "alternatives": a3}) 
               
            # ------------------- 복합 지성 (CombinationOily) -------------------
            if skin_type == 'CombinationOily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "깨끗한 세안으로 하루를 상쾌하게 시작해요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '스킨/토너' 
                    AND sub_category IN ('모공', '수분')  
                    AND (name LIKE '%병풀%' OR name LIKE '%저분자%' OR name LIKE '%수딩%' OR name LIKE '%녹차%' OR name LIKE '%그린%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "산뜻하지만 내 피부에 필요한 수분을 채워줘요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('모공', '수분')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%로션%' OR  name LIKE '%젤%')
                    AND (name LIKE '%병풀%' OR name LIKE '%히알루론산%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "유분이 많은 T존은 가볍게, 건조한 U존은 얇게 덧발라주세요.", "primary_recommendation": p3, "alternatives": a3}) 


    #겨울   
    if current_season == 'winter': 
        # 고민 : 계절 -> 주름,탄력 ox -> 피부타입
        if has_wrinkle_elasticity_moisture_concern: 
            # ------------------- 💧 건성 (Dry) -------------------
            if skin_type == 'Dry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%젤%' OR name LIKE '%워터%' OR name LIKE '%크림%') 
                    AND name LIKE '%약산성%'
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "피부에 자극을 주지 않는 약산성 클렌저를 사용하세요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%팩%' AND name NOT LIKE '%폼%'
                    AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "추운 겨울, 안티에이징 제품으로 주름과 탄력을 관리해요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%판테놀%' OR name LIKE '%고보습%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "안티에이징 제품으로 탄력있고 촉촉한 피부를 느껴보세요.", "primary_recommendation": p3, "alternatives": a3}) 

            # ------------------- ✨ 지성 (Oily) -------------------
            if skin_type == 'Oily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%') 
                    AND (name LIKE '%티트리%' OR name LIKE '%그린%' OR name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "상쾌한 세안으로 기분 좋은 하루를 시작하세요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('안티에이징', '수분', '모공')                
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%나이아신%' OR name LIKE '%나이아신%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%저분자%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "세안 후에는 끈적임 없이 가볍게 흡수되는 제품으로 주름과 탄력을 관리해요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%수분 크림%' OR name LIKE '%젤%' OR name LIKE '%워터 크림%' OR name LIKE '%로션%')
                    AND (name LIKE '%세라마이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "피부 겉은 산뜻하게 속은 촉촉하게 채워요.", "primary_recommendation": p3, "alternatives": a3}) 
                    
            # ------------------- ⚖️ 중성 (Normal) -------------------
            if skin_type == 'Normal':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '기본')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "가볍게 물세안이나 순한 클렌저를 사용해주세요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('수분', '안티에이징', '리페어')  
                    AND (name LIKE '%나이아신%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%' OR name LIKE '%히알루론산%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "차오르는 수분과 탄력감을 느껴보세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '보습')  
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%히알루론산%' OR name LIKE '%항%' OR name LIKE '%스쿠알란%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "크림으로 수분 장벽을 지키고 피부의 밸런스를 맞춰요.", "primary_recommendation": p3, "alternatives": a3}) 
            # ------------------- 복합 건성 (CombinationDry) -------------------
            if skin_type == 'CombinationDry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%' OR name LIKE '%히알루론산%' OR name LIKE '%수분%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "건조하지 않게 노폐물만 가볍게 씻어내요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')  
                    AND (name LIKE '%병풀%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "내 피부의 건조한 부분을 수분으로 채워줘요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '보습')  
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "T존은 가볍게, U존은 보습을 위해 얇게 여러 번 발라주세요..", "primary_recommendation": p3, "alternatives": a3}) 
               
            # ------------------- 복합 지성 (CombinationOily) -------------------
            if skin_type == 'CombinationOily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%모닝%' OR name LIKE '%저자극%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "T존은 번들거림 없이, U존은 촉촉하게", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category In ('스킨/토너', '에센스/앰플/세럼') 
                    AND sub_category IN ('안티에이징', '모공', '수분')  
                    AND (name LIKE '%병풀%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "춥고 건조한 겨울, 부족한 수분을 채워요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '모공', '수분')  
                    AND (name LIKE '%로션%' OR name LIKE '%젤%' OR name LIKE '%크림%')
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%라이트%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "수분이 날아가지 않도록 크림을 발라줘요.", "primary_recommendation": p3, "alternatives": a3}) 
        
        # 고민 : 수분 -> 피부 타입과 연관ㅇ
        elif has_moisture_concern: 
            # ------------------- 💧 건성 (Dry) -------------------
            if skin_type == 'Dry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%젤%' OR name LIKE '%워터%') 
                    AND (name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "악산성 제품을 사용해 피부에 자극을 줄여요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category In ('에센스/앰플/세럼')
                    AND sub_category IN ('수분', '보습')
                    AND (name LIKE "%스킨%" OR name LIKE "%토너%" OR name LIKE '%세럼%')
                    AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%나이아신%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 스킨 케어", "step_description": "건조한 피부를 위해 수분을 피부 속부터 꼼꼼히 채워요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('수분', '보습')
                    AND (name LIKE '%세라마이드%' OR name LIKE '%스쿠알란%' OR name LIKE '%히알루론산%' OR name LIKE '%고보습%' OR name LIKE '%리치%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "촉촉한 피부를 위해 크림을 꼼꼼히 발라요.", "primary_recommendation": p3, "alternatives": a3}) 

            # ------------------- ✨ 지성 (Oily) -------------------
            if skin_type == 'Oily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '기본', '보습') 
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%') 
                    AND (name LIKE '%티트리%' OR name LIKE '%그린%' OR name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "겨울에는 건조하지 않게 가볍게 세안을 해요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '스킨/토너' 
                    AND sub_category IN ('수분', '기본', '보습')                
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%그린%' OR name LIKE '%녹차%' OR name LIKE '%히알루론산%' OR name LIKE '%병풀%' OR name LIKE '%히알루론산%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "부족한 수분은 채우고 유분은 덜어내요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%수분 크림%' OR name LIKE '%젤%' OR name LIKE '%워터 크림%' OR name LIKE '%로션%')
                    AND (name LIKE '%녹차%' OR name LIKE '%병풀%' OR name LIKE '%나이아신%' OR name LIKE '%그린%'  OR name LIKE '%알로에%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "촉촉한 크림으로 마무리:유수분 밸런스를 맞춰요.", "primary_recommendation": p3, "alternatives": a3}) 
                    
            # ------------------- ⚖️ 중성 (Normal) -------------------
            if skin_type == 'Normal':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '기본',' '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "가볍게 물세안이나 순한 클렌저 사용하여 피부밸런스를 유지해요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '스킨케어'
                    AND middle_category = '스킨/토너'
                    AND sub_category IN ('수분', '기본',' '보습')  
                    AND (name LIKE '%저분자%' OR name LIKE '%병풀%' OR name LIKE '%히알루론산%' OR name LIKE '%녹차%'OR name LIKE '%그린%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "잠자는 동안 마른 수분을 채워요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '스킨케어'
                    AND middle_category = '크림'
                    AND sub_category IN ('수분', '기본',' '보습')   
                    AND (name LIKE '%펩타이드%' OR name LIKE '%나이아신%' OR name LIKE '%히알루론산%' OR name LIKE '%병풀%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "차가운 바람에 보호할 수 있게 크림을 발라줘요.", "primary_recommendation": p3, "alternatives": a3}) 
           
           
            # ------------------- 복합 건성 (CombinationDry) -------------------
            if skin_type == 'CombinationDry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '보습')   
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND name LIKE '%약산성%' 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "약산성 클렌저로 가볍게 씻어내요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '에센스/앰플/세럼')
                    AND sub_category IN ('수분', '보습')  
                    AND (name LIKE '%병풀%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "피부 속부터 꼼꼼하게 수분을 채워요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('수분', '보습')  
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "건조한 U존에는 적은 양으로 한번 더 덧발라주세요.", "primary_recommendation": p3, "alternatives": a3}) 
               
            # ------------------- 복합 지성 (CombinationOily) -------------------
            if skin_type == 'CombinationOily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "약산성 클렌저로 노폐물만 가볍게 씻어내요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '스킨/토너' 
                    AND sub_category IN ('모공', '수분')  
                    AND (name LIKE '%병풀%' OR name LIKE '%저분자%' OR name LIKE '%수딩%' OR name LIKE '%녹차%' OR name LIKE '%그린%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "내 피부에 부족한 수분감을 채워요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('모공', '수분')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%로션%' OR  name LIKE '%젤%')
                    AND (name LIKE '%병풀%' OR name LIKE '%히알루론산%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "번들거리지 않게 부족한 수분을 채워줘요.", "primary_recommendation": p3, "alternatives": a3}) 
        
    # 환절기        
    else:
        # 고민 : 계절 -> 주름,탄력 ox -> 피부타입
        if has_wrinkle_elasticity_moisture_concern: 
            # ------------------- 💧 건성 (Dry) -------------------
            if skin_type == 'Dry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%밀크%' OR name LIKE '%젤%' OR name LIKE '%워터%' OR name LIKE '%크림%') 
                    AND (name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "약산성 클렌저를 사용해 피부 장벽을 보호해요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%히알루론산%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%병풀%' OR name LIKE '%나이아신%' OR name LIKE '%어성초%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "건조함 없이 촉촉하고 편안한 피부를 느껴봐요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%병풀%' OR name LIKE '%나이아신%' OR name LIKE '%어성초%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "민감해진 피부를 진정시켜요.", "primary_recommendation": p3, "alternatives": a3}) 

            # ------------------- ✨ 지성 (Oily) -------------------
            if skin_type == 'Oily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%') 
                    AND (name LIKE '%티트리%' OR name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "저자극 클렌저를 사용해 가볍게 세안해요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('안티에이징', '수분', '모공')                
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%나이아신%' OR name LIKE '%병풀%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%저분자%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "자극 없이 편안한 피부를 느껴봐요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%수분 크림%' OR name LIKE '%젤%' OR name LIKE '%워터 크림%' OR name LIKE '%로션%')
                    AND (name LIKE '%세라마이드%' OR name LIKE '%아데노신%' OR name LIKE '%병풀%' OR name LIKE '%나이아신%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "안티에이징 제품으로 예민한 피부를 관리해요.", "primary_recommendation": p3, "alternatives": a3}) 
                    
            # ------------------- ⚖️ 중성 (Normal) -------------------
            if skin_type == 'Normal':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '기본')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "물세안이나 저자극 클렌저로 세안하세요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category In ('에센스/앰플/세럼') 
                    AND sub_category IN ('수분', '안티에이징', '리페어')  
                    AND (name LIKE '%나이아신%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%병풀%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%' OR name LIKE '%히알루론산%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "민감한 피부에 영양을 더해요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%병풀%' OR name LIKE '%나이아신%' OR name LIKE '%히알루론산%' OR name LIKE '%스쿠알란%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "환절기, 피부 지킴이.", "primary_recommendation": p3, "alternatives": a3}) 
            # ------------------- 복합 건성 (CombinationDry) -------------------
            if skin_type == 'CombinationDry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "약산성 클렌저로 기분좋은 세안을 시작해요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category In ('에센스/앰플/세럼') 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')  
                    AND (name LIKE '%병풀%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%병풀%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "세안 후에는 안티에이징과 함께 파부 장벽을 강화해요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%세라마이드%' OR name LIKE '%병풀%' OR name LIKE '%어성초%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "민감한 피부 진정템.", "primary_recommendation": p3, "alternatives": a3}) 
               
            # ------------------- 복합 지성 (CombinationOily) -------------------
            if skin_type == 'CombinationOily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%저자극%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "가벼운 클렌징으로 산뜻한 하루를 시작해요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '스킨/토너' 
                    AND sub_category IN ('안티에이징', '모공', '수분')  
                    AND (name LIKE '%병풀%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%병풀%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "부드러운 피부결을 만들어요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '모공', '수분')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%로션%' OR  name LIKE '%젤%')
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%병풀%' OR name LIKE '%나이아신%' OR name LIKE '%라이트%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "환절기, 번들거리지 않게 보습에 집중해보아요.", "primary_recommendation": p3, "alternatives": a3}) 
        
        # 고민 : 수분 -> 피부 타입과 연관ㅇ
        elif has_moisture_concern: 
            # ------------------- 💧 건성 (Dry) -------------------
            if skin_type == 'Dry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%젤%' OR name LIKE '%워터%' OR name LIKE '%크림%') 
                    AND (name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "가벼운 물세안이나 저자극 클렌징을 해요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category In ('스킨/토너', '에센스/앰플/세럼')
                    AND sub_category IN ('수분', '보습', '기본')
                    AND (name LIKE "%스킨%" OR name LIKE "%토너%" OR name LIKE '%세럼%')
                    AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%나이아신%' OR name LIKE '%병풀%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "건조함 No, 촉촉함 Yes", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('수분', '보습', '기본')
                    AND (name LIKE '%세라마이드%' OR name LIKE '%스쿠알란%' OR name LIKE '%히알루론산%' OR name LIKE '%고보습%' )
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "안티에이징 효과와 함께 피부 장벽을 보호해요.", "primary_recommendation": p3, "alternatives": a3}) 

            # ------------------- ✨ 지성 (Oily) -------------------
            if skin_type == 'Oily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '기본', '보습') 
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%') 
                    AND (name LIKE '%티트리%' OR name LIKE '%그린%' OR name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "밤사이 쌓인 노폐물만 씻어내요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE middle_category = '스킨/토너' 
                    AND sub_category IN ('수분', '기본', '보습')                
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%그린%' OR name LIKE '%녹차%' OR name LIKE '%병풀%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "민감해진 피부를 진정시키고 관리해요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE middle_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%수분 크림%' OR name LIKE '%젤%' OR name LIKE '%워터 크림%' OR name LIKE '%로션%')
                    AND (name LIKE '%녹차%' OR name LIKE '%병풀%' OR name LIKE '%나이아신%' OR name LIKE '%그린%'  OR name LIKE '%알로에%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "환절기 맞춤 수분 케어", "primary_recommendation": p3, "alternatives": a3}) 
                    
            # ------------------- ⚖️ 중성 (Normal) -------------------
            if skin_type == 'Normal':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '기본',' '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "가볍게 물세안 또는 순한 클렌저 사용하기!", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '스킨케어'
                    AND middle_category = '에센스/앰플/세럼'
                    AND sub_category IN ('수분', '기본',' '보습')  
                    AND (name LIKE '%저분자%' OR name LIKE '%병풀%' OR name LIKE '%히알루론산%' OR name LIKE '%녹차%' OR name LIKE '%그린%' OR name LIKE '%병풀%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "피부 안정 집중 관리!", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '스킨케어'
                    AND middle_category = '크림'
                    AND sub_category IN ('수분', '기본',' '보습')   
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%히알루론산%' OR name LIKE '%항%' OR name LIKE '%병풀%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "유수분 밸런스를 지키며 피부 장벽을 강화해요.", "primary_recommendation": p3, "alternatives": a3}) 
           
           
            # ------------------- 복합 건성 (CombinationDry) -------------------
            if skin_type == 'CombinationDry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '보습')   
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "피부에 자극이 되지 않게 가볍게 세안해요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '에센스/앰플/세럼'
                    AND sub_category IN ('수분', '보습')  
                    AND (name LIKE '%병풀%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%어성초%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "민감해진 내 피부를 진정시켜요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('수분', '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%병풀%' OR name LIKE '%어성초%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "민감해진 피부 완화하기.", "primary_recommendation": p3, "alternatives": a3}) 
               
            # ------------------- 복합 지성 (CombinationOily) -------------------
            if skin_type == 'CombinationOily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('수분', '모공')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%저자극%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "자극없는 세안으로 내 피부를 지켜요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '스킨/토너' 
                    AND sub_category IN ('모공', '수분')  
                    AND (name LIKE '%병풀%' OR name LIKE '%저분자%' OR name LIKE '%수딩%' OR name LIKE '%녹차%' OR name LIKE '%그린%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "편안한 피부 집중 케어.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('모공', '수분')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%로션%' OR name LIKE '%젤%' OR name LIKE '%크림%')
                    AND (name LIKE '%병풀%' OR name LIKE '%히알루론산%' OR name LIKE '%세라마이드%')
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "탄탄한 피부 장벽 완성.", "primary_recommendation": p3, "alternatives": a3}) 
