import bpy
from bpy.types import Operator
import requests
import json
import os


class PIE_Custom_Scripts_EmptyToCollection(bpy.types.Operator):
    bl_idname = "pie.empty_to_collection"
    bl_label = "选择父子级到集合"
    bl_description = "将选择的空物体绑定的父子级创建到集合"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            name  = ob.name
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            bpy.data.objects[name].select_set(True)
            bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name=name)
        return {"FINISHED"}

class PIE_Custom_Scripts_CleanSameMatTex(bpy.types.Operator):
    bl_idname = "pie.clean_same_material_texture"
    bl_label = "清理同名材质槽贴图"
    bl_description = "清理.001类似的材质和贴图.注意使用！"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
        # return self.execute(context)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text="仅适用于导入模型！", icon="ERROR")

    def execute(self, context):
        import re
        selected_objects = bpy.context.selected_objects
        def change_mat(active_mat_name):
            if "." in active_mat_name:
                orgin_mat = active_mat_name.split('.',1)[0]
                bpy.ops.view3d.materialutilities_replace_material(
                matorg= active_mat_name,
                matrep=orgin_mat, all_objects=True, update_selection=False)
        # 遍历每个选中的物体
        for obj in selected_objects:
            # 将当前物体设置为激活物体
            bpy.context.view_layer.objects.active = obj
            active_object = bpy.context.active_object
            if active_object is not None and active_object.material_slots:
                print("Active object's material names:")
                # 遍历每个材质槽
                for slot in active_object.material_slots:
                    # 打印材质名称
                    if slot.material:  # 确保材质槽不为空
                        active_mat_name = slot.material.name
                        change_mat(active_mat_name)
        # 正则表达式，用于匹配以点号开头，后跟三个数字的模式
        pattern = re.compile(r"\.\d{3}$")
        # 遍历所有的贴图
        for image in bpy.data.images:
            # 使用正则表达式搜索后缀
            new_name = re.sub(pattern, '', image.name)
            # 如果名称被修改，则更新贴图名称
            if new_name != image.name:
                image.name = new_name

        return {"FINISHED"}

class PIE_Quick_RedHaloM2B(bpy.types.Operator):
    bl_idname = "pie.quick_redhalom2b"
    bl_label = "导入Max导出物体"
    bl_description = "快速通过RedHaloM2B插件导入再MAX中已选择导出的物体"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            bpy.ops.redhalo.maxfilebrower(onlyImport = True)
        except:
            pass
        return {"FINISHED"}
    
global API_KEY, SECRET_KEY
# API_KEY = "CE3ANxCcgsUaZKUKNn5y2yYi"
# SECRET_KEY = "QHbZsyLPBdIBZT3M0uO2Ec09fnBdxJih"
API_KEY = ""
SECRET_KEY = ""

def get_access_token(api,secret):
    """
    使用 AK,SK 生成鉴权签名(Access Token)
    :return: access_token,或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": api, "client_secret": secret}
    response = requests.post(url, params=params).json()
    return response.get("access_token")

def translate_text(access_token,text, from_lang='en', to_lang='zh'):
    """
    使用百度翻译API进行翻译
    """
    if access_token is None:
        print("获取access_token失败")
        return text

    url = f"https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token={access_token}"
    
    payload = json.dumps({
        "q": text,
        "from": from_lang,
        "to": to_lang
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    result = response.json()
    
    if 'result' in result and 'trans_result' in result['result']:
        return result['result']['trans_result'][0]['dst']
    else:
        print("翻译失败：", result)
        return text

settings_file_path = os.path.join(bpy.utils.resource_path('USER'), "config","wxz_pie_menu_settings.txt")

class PIE_Custom_Scripts_Context_Translate(bpy.types.Operator):
    bl_idname = "pie.context_translate"
    bl_label = "翻译选择的指定内容"
    bl_description = "仅支持 英->中"
    bl_options = {"REGISTER","UNDO"}

    trans_ob_text: bpy.props.BoolProperty(name="文本物体")
    trans_collection: bpy.props.BoolProperty(name="集合")
    baidu_api_key : bpy.props.StringProperty(name="百度API")
    baidu_secret_key : bpy.props.StringProperty(name="百度SECRET")

    def execute(self, context):
        api = self.baidu_api_key
        key = self.baidu_secret_key
         # 保存属性到JSON文件
        data = {
            'baidu_api_key': api,
            'baidu_secret_key': key,
        }
        if len(api+key)>2:
            with open(settings_file_path, 'w') as outfile:
                json.dump(data, outfile)
                
        access_token = get_access_token(api,key)

        if self.trans_ob_text:
            # 翻译场景中的所有文本对象
            for obj in bpy.context.selected_objects:
                if obj.type == 'FONT':
                    # 获取当前文本内容
                    original_text = obj.data.body
                    print(f"原始文本: {original_text}")
                    # 翻译文本
                    translated_text = translate_text(access_token,original_text)
                    print(f"翻译文本: {translated_text}")
                    # 更新文本对象的内容
                    obj.data.body = translated_text
        if self.trans_collection:
            # 遍历所有集合
            for collection in bpy.data.collections:
                # 检查集合中是否有选中的对象
                selected_objects = [obj for obj in collection.objects if obj.select_get()]
                # 如果至少有一个对象被选中，我们认为集合也被选中
                if selected_objects:
                    original_name = collection.name
                    print(f"原始集合名称: {original_name}")
                    # 翻译集合名称
                    translated_name = translate_text(access_token, original_name)
                    print(f"翻译后的集合名称: {translated_name}")
                    # 更新集合的名称
                    collection.name = translated_name
                    return {"FINISHED"}
        
    def invoke(self, context, event):
        # 从JSON文件加载属性值（如果文件存在）
        if os.path.exists(settings_file_path):
            with open(settings_file_path, 'r') as infile:
                data = json.load(infile)
                self.baidu_api_key = data.get('baidu_api_key', '')
                self.baidu_secret_key = data.get('baidu_secret_key', '')
                print(data)
        return context.window_manager.invoke_props_dialog(self)
       
    def draw(self, context):
        layout = self.layout
        layout.scale_x = 2
        box = layout.box()
        row = box.row()
        row.prop(self,"baidu_api_key")
        row = box.row()
        row.prop(self,"baidu_secret_key")
        row = layout.box().row()
        row.prop(self,"trans_ob_text")
        row.prop(self,"trans_collection")
        




classes = [
    PIE_Custom_Scripts_EmptyToCollection,
    PIE_Custom_Scripts_CleanSameMatTex,
    PIE_Quick_RedHaloM2B,
    PIE_Custom_Scripts_Context_Translate,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()