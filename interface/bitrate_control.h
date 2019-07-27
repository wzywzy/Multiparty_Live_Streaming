#include <algorithm>
#include <string.h>
class Reciever//接受方数据
{
public:
	int id;
	int count;
	int * buffer; //缓存中对应每个发送者的帧数,如有n个用户，则buffer中有n个元素，若本用户id是k，则在n中第k个恒为0，下同 
	int * buffersize; //缓存中对应每个发送者的帧数据量 
	int * delay;
	Reciever();
	Reciever(int user);
	int update(int id, int *n_buffer,int *n_buffersize,int *n_delay);
	~Reciever();
};
class Multilive
{
private:
	int * bitrate_list; //存放码率表
	int * user_sort_out; //存放算法输出 
	int * last_buffer;  //上次算法运行时地缓存情况
	int * buffer_error_sum;  //积累的误差
	int * m_QoE_matrix; //qoe系数矩阵
	int m_usercount; //用户数
public:
	//Multilive(int usercount);	//只输入用户数，qoe默认 
	Multilive(int usercount,int* QoE_matrix); //输入用户数和其对应qoe
	~Multilive();	//析构函数，释放内存 
	int estimate(int* throughput);	//根据吞吐量预估网速 
	int optimize_solve(int **thp_down,int  **thp_up);	//最优化算法，通过上下行吞吐情况预测规划每一对的最优码率 
	int buffer_feedback(int *buffersize, int **thp_down,int gap); //反馈调节，获取reciever的数据，同时利用历史数据和带宽综合反馈 
	int	*stream_sort(int  stream_count, int (*QoE)(int recieverid, int senderid, int bitrate));//聚类算法，把多路码率需求针对某一发送端聚类为较少路数,并返回最终结果
};
