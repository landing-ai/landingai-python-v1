import logging
import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageChops

from landingai.predict import OcrPredictor, Predictor
from landingai.visualize import overlay_predictions

_API_KEY = "v7b0hdyfj6271xy2o9lmiwkkcbdpvt1"
_API_SECRET = "ao6yjcju7q1e6u0udgwrgknhrx6m4n1o48z81jy6huc059gne047l4fq3u1cgq"
_EXPECTED_VP_PREDS = [
    {
        "label_name": "Green Field",
        "label_index": 3,
        "score": 0.8484444637722576,
        "encoded_mask": "169Z22N48Z164N104Z20N43Z30N6Z16N781Z10N359Z22N48Z164N104Z20N43Z30N6Z16N781Z10N359Z22N48Z164N104Z20N43Z30N6Z16N781Z10N359Z22N48Z164N104Z20N43Z30N6Z16N781Z10N359Z22N48Z164N104Z20N43Z30N6Z16N781Z10N359Z22N48Z164N104Z20N43Z30N6Z16N781Z10N359Z22N48Z164N104Z20N43Z30N6Z16N781Z10N359Z22N48Z164N104Z20N43Z30N6Z16N781Z10N359Z22N48Z164N112Z8N49Z26N10Z16N779Z10N359Z22N48Z164N112Z8N49Z26N10Z16N779Z10N359Z22N46Z164N175Z22N10Z16N779Z8N361Z22N46Z164N175Z22N10Z16N779Z8N361Z22N46Z164N177Z18N14Z14N779Z8N361Z22N46Z164N177Z18N14Z14N779Z8N361Z22N44Z162N183Z14N18Z14N777Z6N363Z22N44Z162N183Z14N18Z14N777Z6N363Z22N42Z90N32Z40N187Z10N20Z16N775Z4N365Z22N42Z90N32Z40N187Z10N20Z16N775Z4N365Z22N40Z88N48Z24N193Z4N26Z14N1144Z22N40Z88N48Z24N193Z4N26Z14N1144Z22N40Z84N60Z6N233Z16N1142Z22N40Z84N60Z6N233Z16N1142Z22N38Z82N303Z18N1140Z22N38Z82N303Z18N1138Z26N36Z76N309Z28N1128Z26N36Z76N309Z28N1128Z28N34Z74N313Z26N1128Z30N32Z72N315Z26N328Z2N798Z30N32Z72N315Z26N328Z2N798Z32N30Z68N321Z24N326Z16N8Z6N772Z32N30Z68N321Z24N326Z16N8Z6N772Z36N26Z18N2Z48N321Z24N324Z36N768Z36N26Z18N2Z48N321Z24N324Z36N768Z38N24Z14N8Z44N325Z22N324Z38N766Z38N24Z14N8Z44N325Z22N324Z38N766Z40N22Z10N14Z42N327Z20N322Z44N762Z40N22Z10N14Z42N327Z20N322Z44N760Z44N20Z10N16Z40N327Z18N324Z46N758Z44N20Z10N16Z40N327Z18N324Z46N760Z44N16Z10N18Z40N329Z16N324Z48N758Z44N16Z10N18Z40N329Z16N324Z48N782Z22N12Z12N20Z36N333Z12N326Z50N780Z22N12Z12N20Z36N333Z12N326Z50N790Z12N10Z14N20Z36N339Z2N330Z52N788Z12N10Z14N20Z36N339Z2N330Z52N792Z10N6Z16N22Z34N671Z54N790Z10N6Z16N22Z34N671Z54N792Z30N22Z34N671Z56N790Z30N22Z34N671Z56N794Z26N22Z32N675Z56N792Z26N22Z32N675Z56N794Z24N24Z28N677Z56N796Z22N24Z26N679Z58N794Z22N24Z26N679Z58N796Z20N26Z22N681Z58N796Z20N26Z22N681Z58N800Z18N24Z22N683Z56N800Z18N24Z22N683Z56N804Z14N24Z22N683Z56N804Z14N24Z22N683Z56N808Z10N24Z20N687Z54N808Z10N24Z20N687Z54N812Z4N28Z18N687Z56N810Z4N28Z18N687Z56N846Z14N689Z54N846Z14N689Z54N852Z4N695Z52N852Z4N695Z52N1553Z50N1553Z50N1555Z48N1555Z48N1557Z44N1559Z44N1561Z42N1561Z42N860Z6N699Z34N862Z10N699Z28N866Z10N699Z28N866Z10N705Z16N872Z10N705Z16N870Z12N1591Z12N1591Z14N1589Z14N1589Z14N1589Z14N1595Z8N1595Z8N8021Z4N1599Z4N1599Z8N1595Z8N1595Z12N313Z4N1274Z12N313Z4N1274Z14N309Z6N1274Z14N309Z6N1276Z16N303Z8N1248Z4N26Z16N72Z16N209Z10N1250Z4N26Z16N72Z16N209Z10N1250Z6N28Z10N62Z36N197Z14N1250Z6N28Z10N62Z36N197Z14N1248Z12N90Z48N66Z6N117Z16N1248Z12N90Z48N66Z6N117Z16N1248Z18N80Z58N54Z16N111Z16N1250Z18N80Z58N54Z16N111Z16N1250Z20N76Z72N38Z22N107Z18N1250Z20N76Z72N38Z22N107Z18N1250Z22N72Z136N103Z20N1250Z22N72Z136N103Z20N1250Z22N72Z136N101Z22N1250Z22N72Z136N101Z22N1250Z24N70Z136N105Z16N1252Z24N70Z136N105Z16N1254Z24N68Z74N24Z36N1377Z24N68Z74N24Z36N1379Z24N64Z64N42Z24N1385Z24N64Z64N42Z24N1385Z26N62Z58N1457Z26N62Z58N1459Z26N60Z52N1465Z26N60Z52N1467Z24N60Z46N1475Z24N58Z44N1477Z24N58Z44N1479Z24N54Z42N1483Z24N54Z42N1485Z22N54Z40N1487Z22N54Z40N1489Z22N54Z38N1489Z22N54Z38N1493Z22N52Z34N1495Z22N52Z34N1497Z26N50Z28N1499Z26N50Z28N1501Z38N38Z20N1507Z38N38Z20N1511Z36N40Z10N1517Z36N40Z10N1519Z36N1567Z36N1569Z36N1567Z36N1569Z36N1567Z36N1567Z38N1565Z38N1565Z40N26Z26N1513Z40N18Z36N1509Z40N18Z36N1509Z38N6Z54N1505Z38N6Z54N1507Z34N10Z56N1503Z34N10Z56N1503Z32N14Z58N1499Z32N14Z58N1499Z30N18Z58N1497Z30N18Z58N1499Z26N22Z56N1499Z26N22Z56N1499Z26N26Z50N1501Z26N26Z50N1501Z26N30Z44N912Z2N589Z26N30Z44N912Z2N591Z22N36Z34N918Z4N589Z22N36Z34N918Z4N589Z22N40Z22N928Z4N587Z22N40Z22N928Z4N587Z22N42Z8N940Z6N585Z22N42Z8N940Z6N585Z22N990Z8N126Z4N453Z22N990Z8N126Z4N453Z22N992Z6N126Z12N447Z20N992Z8N124Z14N445Z20N992Z8N124Z14N445Z18N994Z10N122Z16N443Z18N994Z10N122Z16N447Z14N996Z10N122Z14N447Z14N996Z10N122Z14N451Z10N996Z12N120Z16N449Z10N996Z12N120Z16N451Z8N996Z16N118Z16N449Z8N996Z16N118Z16N453Z2N1000Z18N114Z20N449Z2N1000Z18N114Z20N1451Z20N112Z24N1447Z20N112Z24N1447Z22N112Z24N1445Z22N112Z24N1447Z20N112Z26N1445Z20N112Z26N1447Z18N110Z28N1447Z18N110Z28N1449Z12N112Z32N1447Z12N112Z32N1451Z2N116Z34N1451Z2N116Z34N1565Z38N1363Z2N196Z42N1363Z2N196Z42N1361Z4N194Z46N1359Z4N194Z46N1355Z8N192Z48N1355Z8N192Z48N1351Z12N192Z36N2Z10N1351Z12N192Z36N2Z10N1351Z12N192Z32N8Z6N1353Z12N192Z32N8Z6N1351Z14N194Z28N10Z6N1351Z14N194Z28N10Z6N1351Z12N196Z26N1369Z12N196Z26N139Z4N1224Z14N198Z20N143Z4N1224Z14N198Z20N134Z13N1224Z14N198Z18N136Z13N1224Z14N198Z18N136Z13N1222Z16N200Z12N130Z23N1222Z16N200Z12N130Z23N1222Z14N204Z8N130Z25N1222Z14N204Z8N130Z25N1222Z14N344Z23N1222Z14N344Z23N1222Z14N354Z13N1222Z14N354Z11N1224Z14N354Z11N1224Z16N352Z11N1224Z16N352Z11N1226Z14N352Z11N1226Z14N352Z9N1228Z14N352Z9N1228Z14N352Z9N1228Z14N352Z9N1228Z14N1589Z14N1589Z14N1591Z12N1591Z12N1593Z10N1593Z10N14771Z8N1595Z8N1593Z10N1593Z10N1593Z10N1591Z12N1591Z12N1591Z12N1591Z12N1593Z10N1593Z10N20651Z6N1597Z6N1595Z8N1595Z8N1593Z12N1591Z12N1591Z12N1589Z16N1587Z16N1587Z16N1587Z16N1589Z14N1589Z14N1591Z12N1591Z12N1593Z8N1595Z8N988Z2N1601Z2N1601Z2N1601Z2N1601Z2N1601Z2N128737Z2N26Z6N1569Z2N26Z6N1569Z2N26Z10N1593Z12N1591Z12N1593Z14N1589Z14N1589Z18N1585Z18N1587Z20N1583Z20N1585Z24N1579Z24N1579Z30N1573Z30N1575Z32N1571Z32N1571Z34N1569Z34N1567Z38N1565Z38N1565Z40N1563Z40N1557Z50N1553Z50N1551Z80N1523Z80N1527Z84N1521Z82N1521Z82N1523Z82N1521Z82N1523Z80N1523Z80N1525Z78N1525Z78N1527Z78N1525Z78N1527Z76N1527Z76N1531Z72N1531Z72N1533Z70N1533Z70N1539Z64N1539Z64N1543Z60N1543Z60N1547Z56N1547Z56N1589Z12N1591Z12N11424Z4N1599Z4N1599Z6N1597Z6N1595Z8N1595Z8N1597Z4N1599Z4N41672Z6N1597Z6N1595Z8N1595Z8N1595Z10N1593Z10N1591Z12N1591Z12N1591Z14N1589Z14N1589Z14N1589Z14N1587Z16N1587Z18N1585Z18N1585Z18N1585Z18N1585Z18N1585Z18N1585Z18N1585Z18N1587Z16N1587Z16N1589Z12N1591Z12N1595Z4N1599Z4N313454Z6N1597Z6N1595Z12N1591Z12N1591Z12N1591Z12N1589Z16N1587Z16N1587Z16N1587Z16N1587Z16N1587Z16N1587Z16N1587Z16N1589Z14N1589Z14N1591Z12N1591Z12N1599Z2N187533Z6N1597Z6N1597Z6N1597Z6N1595Z10N1593Z10N1593Z10N1593Z10N1593Z10N1593Z12N1591Z12N1589Z14N1589Z14N1589Z14N1589Z14N1589Z16N1587Z16N1587Z16N1587Z16N1589Z16N1587Z16N1587Z18N1585Z18N1585Z20N1583Z20N1583Z20N1583Z20N1583Z22N1581Z22N1583Z22N1581Z22N1581Z22N1581Z22N1581Z24N1579Z26N1577Z26N1577Z26N1577Z26N1579Z26N1577Z26N1577Z30N1573Z30N1573Z32N1571Z32N1571Z34N1569Z34N1571Z34N1569Z34N1571Z32N1571Z32N1573Z30N1573Z30N1575Z30N1573Z30N1573Z30N1573Z30N1575Z28N1575Z28N1575Z28N1575Z28N1575Z28N1577Z26N1577Z26N1579Z24N1579Z24N1579Z22N1581Z22N1587Z14N1589Z14N112643Z6N1597Z6N1595Z12N1591Z12N1591Z14N1589Z14N1589Z16N1587Z16N1585Z20N1583Z20N1583Z22N1581Z22N1581Z24N1579Z24N1579Z26N1577Z26N1577Z28N1575Z28N1577Z28N1575Z28N1579Z22N1581Z22N1583Z18N1589Z12N1591Z12N1593Z6N1597Z6N162107Z26N1577Z26N1557Z46N1557Z46N1553Z50N1553Z50N1551Z52N1551Z52N1551Z52N1551Z52N1551Z52N1551Z52N1553Z50N1553Z50N1555Z48N1555Z48N1557Z46N1557Z46N1559Z44N1559Z44N1563Z40N1563Z40N1565Z38N1569Z34N1569Z34N1569Z34N1569Z34N1571Z32N1571Z32N1571Z32N1571Z32N1571Z32N1571Z32N1573Z30N1573Z30N1573Z30N1573Z30N1573Z30N1573Z30N1573Z30N1573Z30N1573Z30N1573Z30N1575Z28N1575Z28N1575Z28N1575Z28N1575Z28N1575Z28N1575Z28N1577Z26N1577Z26N1577Z26N1577Z26N1577Z26N1577Z26N1579Z24N1579Z24N1579Z24N1579Z24N1581Z22N1581Z22N1581Z22N1581Z22N1583Z20N1583Z20N1583Z20N1583Z20N1585Z18N1585Z18N1587Z16N1587Z16N1587Z16N1589Z14N1589Z14N1591Z12N1591Z12N1595Z8N1595Z8N34229Z30N66Z6N1501Z30N66Z6N1497Z40N54Z10N1499Z40N54Z10N1497Z50N44Z8N1501Z50N44Z8N1497Z58N38Z10N1497Z58N38Z10N1493Z66N30Z12N1495Z66N30Z12N1489Z74N26Z12N1491Z74N26Z12N1489Z78N22Z14N1489Z78N22Z14N1485Z62N2Z16N24Z12N1487Z62N2Z16N24Z12N1144Z24N317Z60N46Z12N1144Z24N317Z60N46Z12N1140Z34N309Z60N50Z10N1140Z34N309Z60N50Z10N1138Z36N20Z2N287Z60N50Z10N1138Z36N20Z2N287Z60N50Z10N1138Z34N22Z2N284Z65N46Z14N22Z6N1108Z32N24Z4N282Z67N44Z16N14Z20N1100Z32N24Z4N282Z67N44Z16N14Z20N1100Z26N30Z4N280Z73N40Z20N4Z32N1094Z26N30Z4N280Z73N40Z20N4Z32N1094Z24N32Z4N280Z75N36Z60N1092Z24N32Z4N280Z75N36Z60N1094Z20N34Z6N278Z77N34Z62N1092Z20N34Z6N278Z77N34Z62N1092Z18N36Z10N272Z81N32Z64N1090Z18N36Z10N272Z81N32Z64N1090Z18N36Z18N264Z81N32Z66N1088Z18N36Z18N264Z81N32Z66N1088Z16N38Z20N260Z83N32Z66N1088Z16N38Z20N260Z83N32Z66N1088Z14N38Z24N258Z83N32Z66N1088Z14N38Z24N258Z83N32Z66N1088Z14N38Z26N256Z83N32Z66N1088Z14N38Z26N256Z83N32Z66N1090Z10N40Z26N256Z81N34Z66N1090Z10N40Z26N256Z81N34Z66N1092Z6N42Z28N254Z81N36Z64N1092Z6N42Z28N254Z81N36Z64N1140Z28N254Z81N36Z64N1140Z28N254Z81N36Z64N1140Z30N252Z81N36Z64N1140Z30N252Z43N2Z34N38Z64N1140Z30N252Z43N2Z34N38Z64N1140Z32N250Z41N4Z34N40Z60N1142Z32N250Z41N4Z34N40Z60N1144Z30N248Z45N2Z34N40Z58N1146Z30N248Z45N2Z34N40Z58N1148Z26N250Z81N42Z52N60Z4N1088Z26N250Z81N42Z52N60Z4N1090Z24N250Z81N44Z46N64Z4N1090Z24N250Z81N44Z46N64Z4N1092Z22N248Z83N48Z34N72Z4N1092Z22N248Z83N48Z34N72Z4N1094Z20N246Z85N52Z24N76Z6N1094Z20N246Z85N52Z24N76Z6N1096Z18N246Z85N56Z10N86Z6N156Z2N938Z18N246Z85N56Z10N86Z6N156Z2N938Z18N244Z87N152Z8N152Z6N936Z18N244Z87N152Z8N152Z6N938Z14N246Z33N10Z42N156Z4N154Z6N938Z14N246Z33N10Z42N156Z4N154Z6N938Z14N244Z35N8Z44N316Z4N938Z14N244Z35N8Z44N316Z4N938Z12N246Z37N2Z48N316Z2N940Z12N246Z37N2Z48N316Z2N940Z12N244Z87N1262Z8N246Z85N1264Z8N246Z85N1264Z8N244Z85N1266Z8N244Z85N1266Z6N244Z85N1268Z6N244Z85N1270Z4N244Z83N1272Z4N244Z83N1272Z4N240Z77N1282Z4N240Z77N1282Z2N238Z71N1292Z2N238Z71N1526Z73N1530Z73N1528Z73N1530Z73N1530Z71N1532Z71N1532Z69N1534Z69N1536Z65N214Z4N1320Z65N214Z4N1320Z65N212Z8N1318Z65N212Z8N1320Z65N84Z4N122Z8N1324Z6N39Z16N82Z8N120Z8N1324Z6N39Z16N82Z8N120Z8N1463Z14N118Z6N1465Z14N118Z6N1459Z22N118Z4N1459Z22N118Z4N1022Z4N429Z24N120Z4N1022Z4N429Z24N120Z4N1024Z4N423Z28N120Z2N1026Z4N423Z28N120Z2N1453Z26N1577Z26N1575Z26N1577Z26N1575Z24N1579Z24N1573Z20N1583Z20N7622Z6N1597Z6N1601Z2N18094Z4N1599Z4N1599Z4N1599Z4N1597Z8N1595Z8N1593Z10N1593Z10N1593Z12N1591Z12N1589Z14N1589Z14N1591Z12N1591Z12N1591Z12N1591Z12N1591Z12N1591Z12N1591Z12N1591Z12N1591Z12N1593Z10N1593Z10N1593Z10N1593Z10N1595Z8N1595Z8N17657Z4N236Z4N1359Z4N236Z4N1357Z6N228Z18N1351Z6N228Z18N1353Z6N224Z20N1589Z10N1593Z10N277932Z",
        "mask_shape": (1539, 1603),
        "num_predicted_pixels": 39711,
        "percentage_predicted_pixels": 0.016096767877967603,
    },
    {
        "label_name": "Brown Field",
        "label_index": 4,
        "score": 0.9469594520537422,
        "mask_shape": (1539, 1603),
        "num_predicted_pixels": 657373,
        "percentage_predicted_pixels": 0.26646472237524105,
    },
    {
        "label_name": "Trees",
        "label_index": 5,
        "score": 0.9759463515311614,
        "mask_shape": (1539, 1603),
        "num_predicted_pixels": 990878,
        "percentage_predicted_pixels": 0.401650252106086,
    },
    {
        "label_name": "Structure",
        "label_index": 6,
        "score": 0.9677068448643612,
        "mask_shape": (1539, 1603),
        "num_predicted_pixels": 765303,
        "percentage_predicted_pixels": 0.3102139142129949,
    },
]


def test_od_predict():
    Path("tests/output").mkdir(parents=True, exist_ok=True)
    # Endpoint: https://app.landing.ai/app/376/pr/11165/deployment?device=tiger-team-integration-tests
    endpoint_id = "db90b68d-cbfd-4a9c-8dc2-ebc4c3f6e5a4"
    # TODO: Replace with v2 API key
    os.environ["landingai_api_key"] = _API_KEY
    os.environ["landingai_api_secret"] = _API_SECRET
    predictor = Predictor(endpoint_id)
    img = np.asarray(Image.open("tests/data/images/cereal1.jpeg"))
    assert img is not None
    # Call LandingLens inference endpoint with Predictor.predict()
    preds = predictor.predict(img)
    assert len(preds) == 3, "Result should not be empty or None"
    expected_scores = [0.9997884631156921, 0.9979170560836792, 0.9976948499679565]
    expected_bboxes = [
        (432, 1035, 651, 1203),
        (1519, 1414, 1993, 1800),
        (948, 1592, 1121, 1797),
    ]
    for i, pred in enumerate(preds):
        assert pred.label_name == "Screw"
        assert pred.label_index == 1
        assert pred.score == expected_scores[i]
        assert pred.bboxes == expected_bboxes[i]
    logging.info(preds)
    img_with_preds = overlay_predictions(predictions=preds, image=img)
    img_with_preds.save("tests/output/test_od.jpg")
    del os.environ["landingai_api_key"]
    del os.environ["landingai_api_secret"]


def test_seg_predict(expected_seg_prediction, seg_mask_validator):
    Path("tests/output").mkdir(parents=True, exist_ok=True)
    # Project: https://app.landing.ai/app/376/pr/26113016987660/deployment?device=tiger-team-integration-tests
    endpoint_id = "72fdc6c2-20f1-4f5e-8df4-62387acec6e4"
    # TODO: Replace with v2 API key
    os.environ["landingai_api_key"] = _API_KEY
    os.environ["landingai_api_secret"] = _API_SECRET
    predictor = Predictor(endpoint_id)
    img = Image.open("tests/data/images/cereal1.jpeg")
    assert img is not None
    preds = predictor.predict(img)
    assert len(preds) == 1, "Result should not be empty or None"
    seg_mask_validator(preds[0], expected_seg_prediction)
    logging.info(preds)
    img_with_masks = overlay_predictions(preds, img)
    img_with_masks.save("tests/output/test_seg.jpg")
    del os.environ["landingai_api_key"]
    del os.environ["landingai_api_secret"]


def test_vp_predict(seg_mask_validator):
    Path("tests/output").mkdir(parents=True, exist_ok=True)
    # Project: https://app.landing.ai/app/376/pr/26098103179275/deployment?device=tiger-example
    endpoint_id = "63035608-9d24-4342-8042-e4b08e084fde"
    # TODO: Replace with v2 API key
    os.environ["landingai_api_key"] = _API_KEY
    os.environ["landingai_api_secret"] = _API_SECRET
    predictor = Predictor(endpoint_id)
    img = np.asarray(Image.open("tests/data/images/farm-coverage.jpg"))
    assert img is not None
    preds = predictor.predict(img)
    assert len(preds) == 4, "Result should not be empty or None"
    for actual, expected in zip(preds, _EXPECTED_VP_PREDS):
        seg_mask_validator(actual, expected)
    logging.info(preds)
    color_map = {
        "Trees": "green",
        "Structure": "#FFFF00",  # yellow
        "Brown Field": "red",
        "Green Field": "blue",
    }
    options = {"color_map": color_map}
    img_with_masks = overlay_predictions(preds, img, options)
    img_with_masks.save("tests/output/test_vp.png")
    expected = Image.open("tests/data/images/expected_vp_masks.png")
    diff = ImageChops.difference(img_with_masks.resize((512, 512)), expected)
    assert diff.getbbox() is None, "Expected and actual images should be the same"
    del os.environ["landingai_api_key"]
    del os.environ["landingai_api_secret"]


def test_class_predict():
    Path("tests/output").mkdir(parents=True, exist_ok=True)
    # Project: https://app.landing.ai/app/376/pr/26119078438913/deployment?device=tiger-team-integration-tests
    endpoint_id = "8fc1bc53-c5c1-4154-8cc1-a08f2e17ba43"
    # TODO: Replace with v2 API key
    os.environ["landingai_api_key"] = _API_KEY
    os.environ["landingai_api_secret"] = _API_SECRET
    predictor = Predictor(endpoint_id)
    img = Image.open("tests/data/images/wildfire1.jpeg")
    assert img is not None
    preds = predictor.predict(img)
    assert len(preds) == 1, "Result should not be empty or None"
    assert preds[0].label_name == "HasFire"
    assert preds[0].label_index == 0
    assert preds[0].score == 0.9956502318382263
    logging.info(preds)
    img_with_masks = overlay_predictions(preds, img)
    img_with_masks.save("tests/output/test_class.jpg")
    del os.environ["landingai_api_key"]
    del os.environ["landingai_api_secret"]


# TODO: re-enable below test after OCR endpoint is deployed to prod
@pytest.mark.skip(reason="OCR endpoint is not deployed to prod yet")
def test_ocr_predict():
    Path("tests/output").mkdir(parents=True, exist_ok=True)
    predictor = OcrPredictor(
        # TODO: replace with a prod key after the OCR endpoint is deployed to prod
        api_key="land_sk_6uttU3npa5V0MUgPWb6j33ZuszsGBqVGs4wnoSR91LBwpbjZpG",
        api_secret="1234",
    )
    img = Image.open("tests/data/images/ocr_test.png")
    assert img is not None
    # Test multi line
    preds = predictor.predict(img, mode="multi-text")
    logging.info(preds)
    expected_texts = [
        "公司名称",
        "业务方向",
        "Anysphere",
        "AI工具",
        "Atomic Semi",
        "芯片",
        "Cursor",
        "代码编辑",
        "Diagram",
        "设计",
        "Harvey",
        "AI法律顾问",
        "Kick",
        "会计软件",
        "Milo",
        "家长虚拟助理",
        "qqbot.dev",
        "开发者工具",
        "EdgeDB",
        "开源数据库",
        "Mem Labs",
        "笔记应用",
        "Speak",
        "英语学习",
        "Descript",
        "音视频编辑",
        "量子位",
    ]
    assert len(preds) == len(expected_texts)
    for pred, expected in zip(preds, expected_texts):
        assert pred.text == expected

    img_with_masks = overlay_predictions(preds, img)
    img_with_masks.save("tests/output/test_ocr_multiline.jpg")
    # Test single line
    preds = predictor.predict(
        img,
        mode="single-text",
        regions_of_interest=[
            [[99, 19], [366, 19], [366, 75], [99, 75]],
            [[599, 842], [814, 845], [814, 894], [599, 892]],
        ],
    )
    logging.info(preds)
    expected = [
        {
            "text": "公司名称",
            "location": [(99, 19), (366, 19), (366, 75), (99, 75)],
            "score": 0.8279303908348083,
        },
        {
            "text": "英语学习",
            "location": [(599, 842), (814, 845), (814, 894), (599, 892)],
            "score": 0.939440906047821,
        },
    ]
    for pred, expected in zip(preds, expected):
        assert pred.text == expected["text"]
        assert pred.location == expected["location"]
        assert pred.score == expected["score"]
    img_with_masks = overlay_predictions(preds, img)
    img_with_masks.save("tests/output/test_ocr_singleline.jpg")
    del os.environ["landingai_api_key"]
    del os.environ["landingai_api_secret"]


# TODO: re-enable below test after OCR endpoint is deployed to prod
@pytest.mark.skip(reason="OCR endpoint is not deployed to prod yet")
def test_ocr_predict():
    Path("tests/output").mkdir(parents=True, exist_ok=True)
    predictor = OcrPredictor(
        # TODO: replace with a prod key after the OCR endpoint is deployed to prod
        api_key="land_sk_6uttU3npa5V0MUgPWb6j33ZuszsGBqVGs4wnoSR91LBwpbjZpG",
        api_secret="1234",
    )
    img = Image.open("tests/data/images/ocr_test.png")
    assert img is not None
    # Test multi line
    preds = predictor.predict(img, mode="multi-text")
    logging.info(preds)
    expected_texts = [
        "公司名称",
        "业务方向",
        "Anysphere",
        "AI工具",
        "Atomic Semi",
        "芯片",
        "Cursor",
        "代码编辑",
        "Diagram",
        "设计",
        "Harvey",
        "AI法律顾问",
        "Kick",
        "会计软件",
        "Milo",
        "家长虚拟助理",
        "qqbot.dev",
        "开发者工具",
        "EdgeDB",
        "开源数据库",
        "Mem Labs",
        "笔记应用",
        "Speak",
        "英语学习",
        "Descript",
        "音视频编辑",
        "量子位",
    ]
    assert len(preds) == len(expected_texts)
    for pred, expected in zip(preds, expected_texts):
        assert pred.text == expected

    img_with_masks = overlay_predictions(preds, img)
    img_with_masks.save("tests/output/test_ocr_multiline.jpg")
    # Test single line
    preds = predictor.predict(
        img,
        mode="single-text",
        regions_of_interest=[
            [[99, 19], [366, 19], [366, 75], [99, 75]],
            [[599, 842], [814, 845], [814, 894], [599, 892]],
        ],
    )
    logging.info(preds)
    expected = [
        {
            "text": "公司名称",
            "location": [(99, 19), (366, 19), (366, 75), (99, 75)],
            "score": 0.8279303908348083,
        },
        {
            "text": "英语学习",
            "location": [(599, 842), (814, 845), (814, 894), (599, 892)],
            "score": 0.939440906047821,
        },
    ]
    for pred, expected in zip(preds, expected):
        assert pred.text == expected["text"]
        assert pred.location == expected["location"]
        assert pred.score == expected["score"]
    img_with_masks = overlay_predictions(preds, img)
    img_with_masks.save("tests/output/test_ocr_singleline.jpg")
