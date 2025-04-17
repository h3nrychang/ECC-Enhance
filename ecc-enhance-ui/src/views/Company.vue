<template>
  <div class="company-container">
    <a-space direction="vertical" style="width: 100%">
      <a-page-header title="企业渗透情况列表" @back="goHome" />

      <a-space wrap>
        <a-button type="primary" @click="handleAdd">添加</a-button>
        <a-upload :before-upload="beforeUpload" :show-upload-list="false">
          <a-button>导入拜访信息</a-button>
        </a-upload>
        <a-button @click="exportData">导出渗透信息</a-button>
      </a-space>

      <a-table
        :dataSource="data"
        :columns="columns"
        :pagination="pagination"
        @change="onTableChange"
        rowKey="id"
        bordered
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button size="small" @click="() => showEditModal(record)">改</a-button>
              <a-popconfirm title="确认删除？" @confirm="() => removeRow(record.id)">
                <a-button size="small" danger>删</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>

      <a-modal v-model:open="editModalVisible" title="编辑企业信息" @ok="submitEdit">
        <a-form layout="vertical">
          <a-form-item label="企业名称">
            <a-input v-model:value="editForm.company_name" />
          </a-form-item>
          <a-form-item label="单位实际人数">
            <a-input v-model:value="editForm.actual_people_count" />
          </a-form-item>
          <a-form-item label="异网运营商">
            <a-input v-model:value="editForm.other_carrier" />
          </a-form-item>
          <a-form-item label="关键人姓名">
            <a-input v-model:value="editForm.key_person_name" />
          </a-form-item>
          <a-form-item label="关键人电话">
            <a-input v-model:value="editForm.key_person_phone" />
          </a-form-item>
          <a-form-item label="友商已有业务">
            <a-input v-model:value="editForm.competitor_services" />
          </a-form-item>
          <a-form-item label="友商合同价格">
            <a-input v-model:value="editForm.competitor_price" />
          </a-form-item>
          <a-form-item label="友商产品到期时间">
            <a-input v-model:value="editForm.competitor_expiry" />
          </a-form-item>
          <a-form-item label="拜访人">
            <a-input v-model:value="editForm.visitor_name" />
          </a-form-item>
          <a-form-item label="备注">
            <a-input v-model:value="editForm.remarks" />
          </a-form-item>
          <a-form-item label="更新时间">
            <a-input v-model:value="editForm.update_time" />
          </a-form-item>
        </a-form>
      </a-modal>
    </a-space>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get, post, del, fileUpload } from '@/util/request'
import { message } from 'ant-design-vue'

const router = useRouter()
const goHome = () => router.push('/')

const data = ref([])
const pagination = ref({
  current: 1,
  pageSize: 20,
  total: 0,
  showTotal: total => `共 ${total} 条`
})

const editModalVisible = ref(false)
const editForm = reactive({})
const editingId = ref(null)

const columns = [
  { title: '企业名称', dataIndex: 'company_name', key: 'company_name' },
  { title: '单位实际人数', dataIndex: 'actual_people_count', key: 'actual_people_count' },
  { title: '异网运营商', dataIndex: 'other_carrier', key: 'other_carrier' },
  { title: '关键人姓名', dataIndex: 'key_person_name', key: 'key_person_name' },
  { title: '关键人电话', dataIndex: 'key_person_phone', key: 'key_person_phone' },
  { title: '友商已有业务', dataIndex: 'competitor_services', key: 'competitor_services' },
  { title: '友商合同价格', dataIndex: 'competitor_price', key: 'competitor_price' },
  { title: '友商产品到期时间', dataIndex: 'competitor_expiry', key: 'competitor_expiry' },
  { title: '拜访人', dataIndex: 'visitor_name', key: 'visitor_name' },
  { title: '备注', dataIndex: 'remarks', key: 'remarks' },
  { title: '更新时间', dataIndex: 'update_time', key: 'update_time' },
  { title: '操作', key: 'action', width: 150 }
]

async function fetchCompanies() {
  const res = await get('/api/company/list', {
    page: pagination.value.current,
    per_page: pagination.value.pageSize
  })
  data.value = res.data?.data || []
  pagination.value.total = res.data?.total || 0
}

function onTableChange(pag) {
  pagination.value.current = pag.current
  pagination.value.pageSize = pag.pageSize
  fetchCompanies()
}

onMounted(() => {
  fetchCompanies()
})

function handleAdd() {
  message.info('添加功能待实现')
}

function showEditModal(row) {
  editingId.value = row.id
  Object.assign(editForm, row)
  editModalVisible.value = true
}

async function submitEdit() {
  const res = await post(`/api/company/${editingId.value}`, editForm)
  message.success('更新成功')
  editModalVisible.value = false
  fetchCompanies()
}

async function removeRow(id) {
  await del(`/api/company/${id}`)
  message.success('删除成功')
  fetchCompanies()
}

async function beforeUpload(file) {
  const formData = new FormData()
  formData.append('file', file)
  await fileUpload('/api/company/import', formData)
  message.success('上传成功')
  fetchCompanies()
  return false
}

function exportData() {
  window.open('/api/company/export')
}
</script>

<style scoped>
.company-container {
  padding: 24px;
  background-color: #fff;
  border-radius: 8px;
}
</style>