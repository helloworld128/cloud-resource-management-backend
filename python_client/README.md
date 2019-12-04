# README

使用 `python-client` 封装的部分调度kubernetes的函数

- `namespace`作为项目名，默认`default`
- pv / pvc / pod名字均为 `pv/pvc/pod-problem_id`
- label 均为 `"problem_id":problem_id` 作为 `selector`

### 函数说明：

1. **Create Functions**
   1. create_namespace(namespace_name="default")
   2. create_namespaced_service(namespace_name="default", service_name="default")
   3. create_persistent_volume(problem_id="default", storage="5Gi")
   4. create_namespaced_persistent_volume_claim(problem_id="default", storage="5Gi", namespace="default")
   5. create_working_namespaced_pod(problem_id="default", storage="5Gi", namespace="default", image="ubuntu")
2. **Delete Functions**
   1. del_persistent_volume(problem_id="default")
   2. del_namespaced_persistent_volume_claim(problem_id="default", namespace_name="default")
3. **Read Functions**
   1. read_namespaced_pod(problem_id="default", namespace_name="default")
4. **List Functions**
   1. list_namespace()
   2. list_persistent_volume()
   3. list_namespaced_persistent_volume_claim(namespace_name="default")
   4. list_namespaced_pod(namespace_name="default")