// Park.vue - 楼园管理页面
<template>
  <div class="park-container">
    <a-space direction="vertical" style="width: 100%">
      <a-page-header title="楼园列表" @back="goHome" />

      <a-space>
        <a-button type="primary" @click="handleAdd">添加</a-button>
        <a-upload :before-upload="beforeUpload" :show-upload-list="false">
          <a-button>批量导入</a-button>
        </a-upload>
      </a-space>

      <a-table :dataSource="data" :columns="columns" rowKey="id" bordered>
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button size="small" @click="() => editRow(record)">修改</a-button>
              <a-popconfirm title="确认删除？" @confirm="() => removeRow(record.id)">
                <a-button size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-space>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get, post, del, fileUpload } from '@/util/request'
import { message, Modal } from 'ant-design-vue'

const router = useRouter()
const goHome = () => router.push('/')

const data = ref([])

const columns = [
  { title: '楼园', dataIndex: 'name', key: 'name' },
  { title: '企业', dataIndex: 'company_name', key: 'company_name' },
  { title: '操作', key: 'action', width: 150 }
]

async function fetchParks() {
  const res = await get('/api/park/list')
  data.value = res.data || []
}

onMounted(() => {
  fetchParks()
})

function handleAdd() {
  Modal.info({
    title: 'TODO',
    content: '添加表单弹窗可在此实现'
  })
}

function editRow(row) {
  Modal.info({
    title: 'TODO',
    content: `编辑 ${row.name}`
  })
}

async function removeRow(id) {
  await del(`/api/park/${id}`)
  message.success('删除成功')
  fetchParks()
}

async function beforeUpload(file) {
  const formData = new FormData()
  formData.append('file', file)
  await fileUpload('/api/park/import', formData)
  message.success('上传成功')
  fetchParks()
  return false
}
</script>

<style scoped>
.park-container {
  padding: 24px;
  background-color: #fff;
  border-radius: 8px;
}
</style>