"""
    自定义的分页组件
    使用需要如下：

# 识图函数中
    引入模块
        from app_test1.my_class.pagination import MyPage

    def tel(request):

        ......

        # 根据实际筛选自己的数据
        queryset = models.mobile_tel.objects.filter(**data_dict).order_by('-status', '-level')

        # 实例化分页对象
        page_obj = MyPage(request,queryset)

        context = {
            'queryset': page_obj.queryset,  # 分页后的数据
            'page_string': page_obj.html(),  # 页码
        }

        return render(request, 'tel.html', context)
# HTML中

# 生成的数据
    {% for item in queryset %}
        <tr>
            <td>{{ item.id }}</td>
            <td>{{ item.mobile }}</td>
            <td>{{ item.price }}</td>
            <td>{{ item.get_level_display }}</td>
            <td>{{ item.get_status_display }}</td>
            <td>
                <a class="btn btn-primary btn-xs" href="/tel/{{ item.id }}/edit/">编辑</a>
                <a class="btn btn-danger btn-xs" href="/tel/{{ item.id }}/delete/" onclick="dete()">删除</a>
            </td>
        </tr>
    {% endfor %}


# 生成的页码
    <ul class="pagination" >
        {{ page_string }}
    </ul>

"""
from django.utils.safestring import mark_safe
from django.http.request import QueryDict
import copy

class MyPage(object):
    def __init__(self,request,queryset,page_size=10,page_param='page',plus=5):
        """
            参数解析：
            page_size 每页展示的条数
            page_param 请求方法默认get
            request 获取当前网页的get和post信息
            queryset 数据搜索之后的内容
            plus 每页显示多少页码
        """
        query_dict=copy.deepcopy(request.GET)
        query_dict._mutable=True
        self.query_dict=query_dict

        self.page_param=page_param
        page = request.GET.get(page_param,"1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page
        self.page_size = page_size
        self.plus = plus
        # 分页的起始值和结束值
        self.start = (page - 1) * page_size
        self.end = page * page_size
        self.page_queryset = queryset[self.start:self.end]

        # 数据总条数
        total_count = queryset.count()

        # 总页码
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        self.total_page_count = total_page_count

    def html(self):
        if self.total_page_count < 2 * self.plus + 1:
            start_page = 1
            end_page = self.total_page_count
        else:
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            else:
                if (self.page + 5) > self.total_page_count:
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus + 1


        page_strlist = []
        # 首页
        self.query_dict.setlist(self.page_param, [1])
        first = '<li class="pointer" style="display: inline-block; vertical-align: middle; margin: 0 2px;"><a href="?{}" style="cursor: pointer; padding: 8px 16px; text-decoration: none; color: #333; border: 1px solid #ddd; border-radius: 4px; display: inline-block; transition: all 0.3s ease; line-height: 1.5;">首页</a></li>'.format(
            self.query_dict.urlencode())
        page_strlist.append(first)

        # 上一页
        if self.page > 1:
            self.query_dict.setlist(self.page_param, [self.page - 1])
            pre = '<li class="pointer" style="display: inline-block; vertical-align: middle; margin: 0 2px;"><a href="?{}" style="cursor: pointer; padding: 8px 16px; text-decoration: none; color: #333; border: 1px solid #ddd; border-radius: 4px; display: inline-block; transition: all 0.3s ease; line-height: 1.5;">上一页</a></li>'.format(
                self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [1])
            pre = '<li class="pointer" style="display: inline-block; vertical-align: middle; margin: 0 2px;"><a href="?{}" style="cursor: pointer; padding: 8px 16px; text-decoration: none; color: #333; border: 1px solid #ddd; border-radius: 4px; display: inline-block; transition: all 0.3s ease; line-height: 1.5;">上一页</a></li>'.format(
                self.query_dict.urlencode())

        page_strlist.append(pre)

        # 内容
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_param, [i])
            if i == self.page:
                ele = '<li class="active" style="display: inline-block; vertical-align: middle; margin: 0 2px;"><a href="?{}" style="padding: 8px 16px; text-decoration: none; background-color: #007bff; color: white; border: 1px solid #007bff; border-radius: 4px; display: inline-block; transition: all 0.3s ease; line-height: 1.5;">{}</a></li>'.format(
                    self.query_dict.urlencode(), i)
            else:
                ele = '<li style="display: inline-block; vertical-align: middle; margin: 0 2px;"><a href="?{}" style="padding: 8px 16px; text-decoration: none; color: #333; border: 1px solid #ddd; border-radius: 4px; display: inline-block; transition: all 0.3s ease; line-height: 1.5;">{}</a></li>'.format(
                    self.query_dict.urlencode(), i)
            page_strlist.append(ele)

        # 下一页
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_param, [self.page + 1])
            nextt = '<li class="pointer" style="display: inline-block; vertical-align: middle; margin: 0 2px;"><a href="?{}" style="cursor: pointer; padding: 8px 16px; text-decoration: none; color: #333; border: 1px solid #ddd; border-radius: 4px; display: inline-block; transition: all 0.3s ease; line-height: 1.5;">下一页</a></li>'.format(
                self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [self.page])
            nextt = '<li class="pointer" style="display: inline-block; vertical-align: middle; margin: 0 2px;"><a href="?{}" style="cursor: pointer; padding: 8px 16px; text-decoration: none; color: #333; border: 1px solid #ddd; border-radius: 4px; display: inline-block; transition: all 0.3s ease; line-height: 1.5;">下一页</a></li>'.format(
                self.query_dict.urlencode())
        page_strlist.append(nextt)

        # 尾页
        self.query_dict.setlist(self.page_param, [self.total_page_count])
        end_ye = '<li class="pointer" style="display: inline-block; vertical-align: middle; margin: 0 2px;"><a href="?{}" style="cursor: pointer; padding: 8px 16px; text-decoration: none; color: #333; border: 1px solid #ddd; border-radius: 4px; display: inline-block; transition: all 0.3s ease; line-height: 1.5;">尾页</a></li>'.format(
            self.query_dict.urlencode())
        page_strlist.append(end_ye)

        # 跳转 - 简化表单样式
        page_tz = '<li class="pointer" style="display: inline-block; vertical-align: middle; margin-left: 30px;"><form class="form-inline" method="get" style="display: inline-flex; align-items: center; gap: 8px; margin: 0;"><div class="form-group" style="margin: 0;"><input class="form-control" type="text" name="page" placeholder="页数" style="width: 60px; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; height: 36px; line-height: 1.5;"></div><button type="submit" class="btn btn-default" style="padding: 6px 12px; background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; height: 36px; line-height: 1.5;">跳转</button></form></li>'
        page_strlist.append(page_tz)

        page_string = mark_safe("".join(page_strlist))
        return page_string