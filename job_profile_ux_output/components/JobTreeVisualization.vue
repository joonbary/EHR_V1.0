
<template>
  <div class="job-tree-container">
    <!-- 헤더 -->
    <div class="tree-header">
      <div class="header-content">
        <h2>
          <i class="fas fa-sitemap"></i>
          직무 체계도
        </h2>
        <p class="subtitle">전체 {{ jobData.job_count }}개 직무를 한눈에 살펴보세요</p>
      </div>
      
      <div class="header-controls">
        <a-space size="middle">
          <a-input-search
            v-model:value="searchValue"
            placeholder="직무명 또는 설명 검색..."
            allow-clear
            enter-button
            size="large"
            style="width: 300px"
            @search="handleSearch"
          />
          
          <a-button-group>
            <a-button 
              :type="viewMode === 'tree' ? 'primary' : 'default'"
              @click="viewMode = 'tree'"
            >
              <i class="fas fa-sitemap"></i>
              트리뷰
            </a-button>
            <a-button 
              :type="viewMode === 'grid' ? 'primary' : 'default'"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
              그리드뷰
            </a-button>
            <a-button 
              :type="viewMode === 'map' ? 'primary' : 'default'"
              @click="viewMode = 'map'"
            >
              <i class="fas fa-project-diagram"></i>
              맵뷰
            </a-button>
          </a-button-group>
        </a-space>
      </div>
    </div>

    <!-- 브레드크럼 -->
    <Transition name="breadcrumb">
      <div v-if="breadcrumbPath.length > 0" class="breadcrumb-container">
        <a-breadcrumb>
          <a-breadcrumb-item href="/">
            <home-outlined />
          </a-breadcrumb-item>
          <a-breadcrumb-item 
            v-for="(item, index) in breadcrumbPath" 
            :key="item.key"
          >
            <strong v-if="index === breadcrumbPath.length - 1">
              {{ item.label }}
            </strong>
            <span v-else>{{ item.label }}</span>
          </a-breadcrumb-item>
        </a-breadcrumb>
      </div>
    </Transition>

    <!-- 메인 콘텐츠 -->
    <div class="tree-content">
      <TreeView 
        v-if="viewMode === 'tree'"
        :tree-data="treeData"
        :expanded-keys="expandedKeys"
        :search-value="searchValue"
        @expand="handleExpand"
        @select="handleNodeSelect"
      />
      
      <GridView 
        v-else-if="viewMode === 'grid'"
        :job-data="jobData"
        :search-value="searchValue"
        @job-select="handleNodeSelect"
      />
      
      <MapView 
        v-else-if="viewMode === 'map'"
        :job-data="jobData"
        :search-value="searchValue"
        @job-select="handleNodeSelect"
      />
    </div>

    <!-- 상세 정보 드로어 -->
    <a-drawer
      v-model:visible="showDetail"
      title="직무 상세 정보"
      placement="right"
      width="600"
      class="job-detail-drawer"
    >
      <template #title>
        <div class="drawer-title">
          <i :class="selectedJob?.icon" :style="{ color: selectedJob?.color }"></i>
          {{ selectedJob?.name }}
        </div>
      </template>
      
      <JobDetailContent 
        v-if="selectedJob"
        :job="selectedJob" 
        :breadcrumb-path="breadcrumbPath" 
      />
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { HomeOutlined } from '@ant-design/icons-vue'
import TreeView from './TreeView.vue'
import GridView from './GridView.vue'
import MapView from './MapView.vue'
import JobDetailContent from './JobDetailContent.vue'

// Props
const props = defineProps({
  jobData: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['job-select'])

// Reactive data
const expandedKeys = ref(['root'])
const searchValue = ref('')
const filteredData = ref([])
const selectedJob = ref(null)
const viewMode = ref('tree')
const showDetail = ref(false)
const breadcrumbPath = ref([])

// Computed
const treeData = computed(() => {
  const data = filteredData.value.length > 0 ? filteredData.value : [props.jobData]
  return data.map(node => transformTreeData(node))
})

// Methods
const transformTreeData = (node, parentPath = []) => {
  const currentPath = [...parentPath, { key: node.id, label: node.name }]
  
  return {
    key: node.id,
    title: node.name,
    icon: node.icon,
    children: node.children?.map(child => transformTreeData(child, currentPath)) || [],
    isLeaf: node.type === 'job_role',
    data: node,
    path: currentPath,
    style: {
      color: node.color
    }
  }
}

const handleNodeSelect = (node, path = []) => {
  selectedJob.value = node
  breadcrumbPath.value = path
  
  if (node.type === 'job_role') {
    showDetail.value = true
    emit('job-select', node)
  }
}

const handleSearch = (value) => {
  if (value) {
    const filtered = filterTreeNodes(props.jobData, value.toLowerCase())
    filteredData.value = filtered ? [filtered] : []
  } else {
    filteredData.value = []
  }
}

const filterTreeNodes = (node, searchText) => {
  const nameMatch = node.name.toLowerCase().includes(searchText)
  const descriptionMatch = node.description.toLowerCase().includes(searchText)
  
  if (node.children && node.children.length > 0) {
    const filteredChildren = node.children
      .map(child => filterTreeNodes(child, searchText))
      .filter(child => child !== null)
    
    if (filteredChildren.length > 0 || nameMatch || descriptionMatch) {
      return { ...node, children: filteredChildren }
    }
  }
  
  return nameMatch || descriptionMatch ? node : null
}

const handleExpand = (keys) => {
  expandedKeys.value = keys
}

// Watch for search changes
watch(searchValue, (newValue) => {
  if (!newValue) {
    handleSearch('')
  }
})
</script>
