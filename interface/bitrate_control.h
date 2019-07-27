#include <algorithm>
#include <string.h>
class Reciever//���ܷ�����
{
public:
	int id;
	int count;
	int * buffer; //�����ж�Ӧÿ�������ߵ�֡��,����n���û�����buffer����n��Ԫ�أ������û�id��k������n�е�k����Ϊ0����ͬ 
	int * buffersize; //�����ж�Ӧÿ�������ߵ�֡������ 
	int * delay;
	Reciever();
	Reciever(int user);
	int update(int id, int *n_buffer,int *n_buffersize,int *n_delay);
	~Reciever();
};
class Multilive
{
private:
	int * bitrate_list; //������ʱ�
	int * user_sort_out; //����㷨��� 
	int * last_buffer;  //�ϴ��㷨����ʱ�ػ������
	int * buffer_error_sum;  //���۵����
	int * m_QoE_matrix; //qoeϵ������
	int m_usercount; //�û���
public:
	//Multilive(int usercount);	//ֻ�����û�����qoeĬ�� 
	Multilive(int usercount,int* QoE_matrix); //�����û��������Ӧqoe
	~Multilive();	//�����������ͷ��ڴ� 
	int estimate(int* throughput);	//����������Ԥ������ 
	int optimize_solve(int **thp_down,int  **thp_up);	//���Ż��㷨��ͨ���������������Ԥ��滮ÿһ�Ե��������� 
	int buffer_feedback(int *buffersize, int **thp_down,int gap); //�������ڣ���ȡreciever�����ݣ�ͬʱ������ʷ���ݺʹ����ۺϷ��� 
	int	*stream_sort(int  stream_count, int (*QoE)(int recieverid, int senderid, int bitrate));//�����㷨���Ѷ�·�����������ĳһ���Ͷ˾���Ϊ����·��,���������ս��
};
