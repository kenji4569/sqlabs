# -*- coding: utf-8 -*-

def get_info_plugin_metas(): 
    return dict(
    plugin_hradio_widget=dict(
        label='Horizontal Radio Widget',
        short_description=T('A radio widget arranging its buttons horizontally'),
        long_description=XML(trans(en="""
%s arranges its radio buttons vertically, which occupies a relatively large area. 
Here we implemented a horizontal radio widget, and further made it clickable for it's labels. 
""",                              ja="""
%sはラジオボタンを垂直に配置するため、少し広めの領域を占めてしまいます。そこで水平のラジオウィジェットを実装し、さらにラベルをクリック可能にしました。
""") % A(T('A built-in radio widget'), _href='http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.RadioWidget-class.html').xml())
    ),
    plugin_multiselect_widget=dict(
        label='Multiple Select Widget',
        short_description=T('A user-friendly multiple options widget'),
        long_description=XML(trans(en="""
%s is made by a single select tag,
which would be difficult to handle when it had many options.
We built more user-friendly multiple select widget with two select tags.
You can choice between horizontal or vertical layout.
""",                                ja="""
%s は単一のセレクトタグからなり、多数のオプションを持つ場合に扱うのが困難になります。
そこで、より使い勝手のよい、２つのセレクトタグからなる複数選択ウィジェットを作成しました。
水平まはた垂直のレイアウトを選ぶことができます。"""
) % A(T('A built-in multiple options widget'), _href='http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.MultipleOptionsWidget-class.html').xml())   
    ),
    plugin_suggest_widget=dict(
        label='Suggest Widget',
        short_description=T('A refined autocomplete widget'),
        long_description=XML(trans(en="""
The suggest widget is an alternative for %s.
It uses %s with some modifications to handle non-us charcters. 
Further, it visualize a selecting status at each typing step.
""",                               ja="""
サジェストウィジェットは%sの代替です。修正した%sを用いて非US文字を扱うことができます。さらに、各タイピングのステップにおける選択状態を可視化します。
""") % (A(T("a built-in autocomplete widget"), _href='http://web2py.com/book/default/chapter/07#Widgets').xml(),
        A('suggest.js', _href='http://www.vulgarisoip.com/2007/08/06/jquerysuggest-11/').xml()))
    ),
    plugin_lazy_options_widget=dict(
        label='Lazy Options Widget',
        short_description=T('A lazy loading options widget triggered by a js event'),
        long_description=XML(trans(en="""
The lazy options widget receives js events and sends ajax requests to populate its select options as in %s.
""",                               ja="""
遅延オプションウィジェットはjsのイベントを受け取ってajaxリクエストを送り、%sのように選択オプションを追加します。
""") % A(T('a built-in options widget'), _href='http://web2py.com/examples/static/epydoc/web2py.gluon.sqlhtml.OptionsWidget-class.html').xml())
    ),
    plugin_anytime_widget=dict(
        label='Anytime Widget',
        short_description=T('A date-time picker widget using anytime.js'),
        long_description=XML(trans(en="""
This plugin provides time, date and datetime picker widgets using %s.
""",                               ja="""
このプラグインは%sを使用して、時刻、日付、日時の選択ウィジェットを提供します。
""") % A('anytime.js', _href='http://www.ama3.com/anytime/').xml() + 
'<br/><span style="color:#D00;">NOTE: Confirm the anytime.js licence. The anytime.js is under the Creative Commons BY-NC-SA 3.0 License.</span>')
    ),
    plugin_color_widget=dict(
        label='Color Widget',
        short_description=T('A color picker widget using colorpicker.js'),
        long_description=XML(trans(en="""
This plugin provides a color picker widget, using %s. Picked color is displayed in forms. 
""",                               ja="""
このプラグインは、%sを用いて色選択ウィジェットを提供します。選択した色はフォームに表示されます。
""") % A('colorpicker.js', _href='http://www.eyecon.ro/colorpicker/').xml())
    ),
    
    plugin_elrte_widget=dict(
        label='elRTE WYSIWYG Widget',
        short_description=T('A WYSIWYG editor widget using elRTE.js'),
        long_description=XML(trans(en="""
A WYSIWYG editor widget using %s. You can specify your language by a contructor argument, and include your image chooser.
""",                               ja="""
%sを使用したWYSIWYGエディターウィジェットです。コンストラクタの引数で使用言語を指定することができ、さらに独自の画像選択機能を組み込むことができます。
""") % A('elRTE.js', _href='http://elrte.org/').xml())
    ),
    plugin_uploadify_widget=dict(
        label='Uploadify Widget',
        short_description=T('A file upload widget using uploadify.js'),
        long_description=XML(trans(en="""
A file upload widget using %s.
The uploadify turns a file input tag into a flash-based file uploader,
which displays a progress bar and enables ajax upload. 
""",                               ja="""
%sを用いたファイルアップロードウィジェットです。uploadifyはファイルのインプタグをflashベースのファイルアップローダーに変換します。これにより、プログレスバーが表示され、ajaxアップロードが可能になります。
""") % A('uploadify.js', _href='http://www.uploadify.com/').xml())
    ),
    
    plugin_tight_input_widget=dict(
        label='Tight Input Widget',
        short_description=T('A size-adjusted input widget'),
        long_description=trans(en="""
An input widget whose size is automatically adjusted to maximum length of its field value
 defined by validators such as IS_LENGTH and IS_INT_IN_RANGE.
The widget works with string, integer, double, and, decimal fields.
""",                           ja="""
自動的にサイズが調整される入力ウィジェットです。IS_LENGTH や IS_INT_IN_RANGE のようなバリデータによって決まるフィールドの値の最大長に応じて変化します。string、integer、double、decimal フィールドに対応しています。
"""),
    ),
    
    plugin_solidform=dict(
        label='Solid Form',
        short_description=T('A custom SQLFORM for denser layout'),
        long_description=trans(en="""
A custom %s for denser layout using multi-line columns. 
You can specify structured fields corresponding to the layout.
Other functionarities are same as SQLFORM, including facotry and readonly forms.
""",                           ja="""
より密なレイアウトのための複合カラムを用いたカスタム%sです。レイアウトに対応する構造化したフィールドを指定することができます。他の機能はSQLFORMと同じで、factoryやreadonlyフォームも利用可能です。
""") % A('SQLFORM', _href='http://web2py.com/book/default/chapter/07#SQLFORM').xml()
    ),
    plugin_notemptymarker=dict(
        label='Not-Empty Marker',
        short_description=T('Add not-empty markers to field labels'),
        long_description=trans(en="""
This plugin automatically attaches not-empty markers to labels of "not-empty" fields of a form, 
based on field validators.
""",                           ja="""
このプラグインは、フィールドのバリデータに基づいて、自動的に必須マークを"必須"フィールドのラベルに付与します。
""")
    ),
    plugin_solidtable=dict(
        label='Solid Table',
        short_description=T('A custom SQLTABLE for denser layout'),
        long_description=XML(trans(en="""
A custom %s for denser layout using multi-line rows. 
You can specify structured fields corresponding to the layout.
The interface of the class keeps backward-compatible to the SQLTABLE,
and enables more flexible customization.
""",                           ja="""
より密なレイアウトのための複合行を用いたカスタム%sです。レイアウトに対応する構造化したフィールドを指定することができます。クラスのインタフェースはSQLTABLEと後方互換を保ちつつ、より柔軟なカスタマイズが可能です。
""") % A('SQLTABLE', _href='http://web2py.com/book/default/chapter/06#Serializing-Rows-in-Views').xml())
    ),
    plugin_paginator=dict(
        label='Paginator',
        short_description=T('A standard paginator'),
        long_description=XML(trans(en="""
A standard paginator which can be used with SQLTABLE. The basic design is inspired by %s.
""",                           ja="""
SQLTABLEとともに用いることができる標準的なページネーターです。基本的な設計は%sを参考にしています。
""") % A(T('this discussion'), _href='http://groups.google.com/group/web2py/browse_frm/thread/d1ec3ded48839071#').xml())
    ),
    plugin_tablescope=dict(
        label='Table Scope',
        short_description=T('A scope selector for table records'),
        long_description=trans(en="""
This plugin provides buttons to select table records by a value of a field,
showing the record count for each value of the field.
""",                           ja="""
このプラグインは、フィールドの値によってテーブルレコードを選択するボタンを提供します。さらに、フィールドの各値に対してレコードの総数を表示します。
"""),
    ),
    plugin_tablecheckbox=dict(
        label='Table Checkbox',
        short_description=T('A table column composed of checkboxes'),
        long_description=trans(en="""
The plugin provides a form object which is an extra table column composed of checkboxes to select multiple records,
and submits selected record ids.
""",                           ja="""
このプラグインは複数のレコードを選択するためのチェックボックスからなる追加のテーブルカラムとしてフォームオブジェクトを提供します。このフォームはレコードのIDを送信します。
"""),
    ),
    plugin_tablepermuter=dict(
        label='Table Permuter',
        short_description=T('Make table rows permutable'),
        long_description=XML(trans(en="""
This plugin a form object which makes table rows permutable using %s, and submits permuted row indices.
""",                           ja="""
このプラグインは%sを用いてテーブルの行を入れ替え可能にするフォームオブジェクトを提供します。このフォームは入れ替えた行のインデックスを送信します。
""") % A('jquery.tablednd.js', _href='http://www.isocra.com/2008/02/table-drag-and-drop-jquery-plugin/').xml())
    ),
    
    
    plugin_solidgrid=dict(
        label='Solid Grid',
        short_description=('A yet another grid. (EXPERIMENTAL)'),
        long_description=XML(trans(en="""
A yet another grid using SOLIDFORM and SOLIDTABLE.  (EXPERIMENTAL)
""",                           ja="""
SOLIDFORM と SOLIDTABLE を用いたもう一つのグリッドです。 (EXPERIMENTAL)
""") )
    ),
    plugin_dialog=dict(
        label='Dialog',
        short_description=('A simple dialog'),
        long_description=XML(trans(en="""
A simple dialog.
""",                           ja="""
シンプルなダイアログです。
""") )
    ),
    plugin_managed_html=dict(
        label='Managed HTML',
        short_description=('An extreme WYSIWYG CMS. (EXPERIMENTAL)'),
        long_description=XML(trans(en="""
A WYSIWYG CMS. Just take a look!  (EXPERIMENTAL)
""",                           ja="""
見たまま編集ができるCMSです。一度見てみてください。 (EXPERIMENTAL)
""") )
    ),
    
    plugin_mptt=dict(
        label='MPTT (Tree Model)',
        short_description='Modified Preorder Tree Traversal (MPTT) implemntation original by django-mptt',
        long_description=XML(trans(en="""
A web2py implemntation of %s, 
which manages tree structured data stored in db with faster selects. 
The program is originated in %s.
""",                           ja="""
%s のweb2py版の実装です。これによりdbに格納された木構造のデータを高速に扱うことができます。プログラムは　%s から派生しています。
""")  % (A('Modified Preorder Tree Traversal (MPTT) algorithm', _href='http://www.sitepoint.com/hierarchical-data-database/'), 
        A('django-mptt', _href='https://github.com/django-mptt/django-mptt/').xml())),
    ),
    plugin_jstree=dict(
        label='Tree Crud',
        short_description='A tree crud using jsTree, fully integrated with the MPTT plugin',
        long_description=XML(trans(en="""
The plugin allows you to CRUD and move tree structured data 
in a fancy ui by using %s. Then, %s could be then included into the plugin as a base tree model.
""",                           ja="""
%s を用いたファンシーなUIで、木構造のデータを、CRUD および 移動できるようになります。
このとき、 %s は木のベースモデルとして、このプラグインへ組み込むことが可能です。
""") % (A('jsTree library', _href='http://www.jstree.com/'),
       A('The MPTT plugin', _href=URL('plugin_mptt', 'index')))),
    ),
    
    plugin_comment_cascade=dict(
        label='Comment Cascade',
        short_description=T('Make facebook-like comment boxes'),
        long_description=trans(en="""The plugin makes ajax-intensive comment boxes for a sort of news feed as in Facebook.""",
                               ja="""Facebookにあるようなニュースフィードに対するAjaxを活用したコメントボックスを作成します。""")
    ),
    plugin_friendship=dict(
        label='Friendship',
        short_description=T('A friendship manager'),
        long_description=trans(en="""The plugin makes friendship relations among users as in Facebook.""",
                               ja="""Facebookにあるようなユーザー間の友達関係を作成します。""")
    ),
    plugin_messaging=dict(
        label='Messaging',
        short_description=T('A direct messaging manager'),
        long_description=trans(en="""The plugin provides direct messaging functionality between users as in Facebook.""",
                               ja="""Facebookにあるようなユーザー間のダイレクト・メッセージ機能を提供します。""")
    ),
    
    plugin_generic_menu=dict(
        label='Generic Menu',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_tagging=dict(
        label='Tagging',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_recommender=dict(
        label='Recommender',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_analytics=dict(
        label='Ananlytics Integration',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_deploytools=dict(
        label='Deploy Tools',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    plugin_testtools=dict(
        label='Test Tools',
        show_image=False,
        short_description='',
        long_description='',
        status='under-construction',
    ),
    
    plugin_catalog=dict(
        label='Catalog',
        show_image=False,
        status='under-construction',
        short_description='A catalog manager shopping (EXPERIMENTAL)',
        long_description=trans(en="""A minimum set of catalog models for shopping (EXPERIMENTAL)"""),
    ),
    plugin_checkout=dict(
        label='Checkout',
        show_image=False,
        short_description='A checkout manager for shopping',
        long_description=trans(en="""A minimum set of checkout models for shopping (Now Developping)"""),
        status='under-construction',
    ),
    
    plugin_rating_widget=dict(
        label='Rating Widget',
        short_description='A rating widget using jquery.rating.js',
        long_description=trans(en="""A rating widget using jquery.rating.js""",
                               ja=""" """),
    ),
)

if request.controller.startswith('plugin_'):
    if request.controller == 'plugin_comment_box':
        session.flash = 'changed from plugin_comment_box to plugin_comment_cascade'
        redirect(URL('plugin_comment_cascade', 'index'))
        
    import os
    from gluon.admin import apath
    from gluon.fileutils import listdir
    from gluon.storage import Storage

    def _to_code(lines, linestart):
        return CODE(''.join(lines[linestart:]).strip(' ').strip('\n').replace('\r', ''))
        
    def _get_code(directory, filename, linestart):
        path = os.path.join(request.folder, directory, filename)
        def _get_code_core():
            if not os.path.exists(path):
                raise HTTP(404)
            f = open(path, 'r')
            lines = f.readlines()
            f.close()
            return _to_code(lines, linestart)
        return cache.ram('code:%s/%s' % (directory, filename), _get_code_core, time_expire=10)

    plugin_name = request.controller
    
    # reload the plugin module
    local_import(plugin_name, reload=MODULE_RELOAD)
    
    # load the controll (usage) code
    controller_code = _get_code('controllers', '%s.py' % plugin_name, linestart=1)
    
    # load the module (source) code
    module_code = _get_code('modules', '%s.py' % plugin_name, linestart=3)
    
    # Get static files
    def _get_statics():
        statics = listdir(apath('sqlabs/static/%s/' % plugin_name, r=request), '[^\.#].*')
        statics = [x.replace('\\','/') for x in statics]
        statics.sort()
        return statics
    statics = cache.ram('statics:%s' % plugin_name, _get_statics, time_expire=10)
    
    info_plugin = get_info_plugin_metas()[plugin_name]
    if info_plugin.get('status') == 'under-construction':
        SHOW_SOCIAL = False
    
    response.web2py_plugins = Storage(
        plugin_name=plugin_name,
        plugin_adopted=info_plugin.get('adopted', False),
        plugin_label=info_plugin['label'],
        plugin_short_description=info_plugin['short_description'],
        plugin_long_description=info_plugin['long_description'],
        controller_code=controller_code,
        module_code=module_code,
        statics=statics,
    )
    response.meta.description = info_plugin['short_description']
    response.image = URL('static', 'images/%s.png' % plugin_name)
    response.view = 'web2py_plugins.html'