#include "bitrate_control.h"
using namespace std;
#include<iostream>
/*Multilive::Multilive(int usercount)
{
	m_usercount = usercount;
	bitrate_list = new int [usercount*usercount];
	memset(bitrate_list,0,usercount*usercount*sizeof(int));
	user_sort_out = new int [usercount*usercount];
	memset(user_sort_out,0,usercount*usercount*sizeof(int));
	last_buffer = new int [usercount*usercount];
	memset(last_buffer,0,usercount*usercount*sizeof(int));
	buffer_error_sum = new int [usercount*usercount];
	memset(buffer_error_sum,0,usercount*usercount*sizeof(int));
	m_QoE_matrix = new int[usercount*usercount];
	for(int i =0;i<usercount*usercount;i++){
		m_QoE_matrix[i]=1;
	}
}*/
Multilive::Multilive(int usercount,int * QoEmatrix)
{
	m_usercount = usercount;
	bitrate_list = new int [usercount*usercount];
	memset(bitrate_list,0,usercount*usercount*sizeof(int));
	user_sort_out = new int [usercount*usercount];
	memset(user_sort_out,0,usercount*usercount*sizeof(int));
	last_buffer = new int [usercount*usercount];
	memset(last_buffer,0,usercount*usercount*sizeof(int));
	buffer_error_sum = new int [usercount*usercount];
	memset(buffer_error_sum,0,usercount*usercount*sizeof(int));
	m_QoE_matrix = new int[usercount*usercount];
	for(int i =0;i<usercount*usercount;i++){
		m_QoE_matrix[i]=QoEmatrix[i];
	};
}
Multilive::~Multilive(){
	delete []bitrate_list;
	delete []user_sort_out;
	delete []last_buffer;
	delete []buffer_error_sum;
	delete []m_QoE_matrix;
}
int Multilive::estimate(int *throughput){
	float sum = 0;
	for (int i = 0; i < 64;i++) {
		sum+=1.0/(float)throughput[i];
	}
	sum = 64 /sum;
	return sum;
}
int Multilive::buffer_feedback(int * buffersize, int ** thp_down, int gap) {
	cout<<"this is for feedback"<<endl;
	for (int i = 0; i < m_usercount; i++) {
		int estimate_bandwidth = estimate(*(thp_down+i));
		for (int j = 0; j < m_usercount; j++) {
			if (i != j) {
				int quantity = buffersize[i*m_usercount+j];
				int sum_qoe = 0;
				for (int k = 0; k < m_usercount; k++) {
					sum_qoe = m_QoE_matrix[k*m_usercount + j];
				}
				int bufferEst = last_buffer[j*m_usercount + i] - (user_sort_out[j * m_usercount + i] - estimate_bandwidth* m_QoE_matrix[i*m_usercount + j] / sum_qoe)*gap;
				last_buffer[j*m_usercount + i] = quantity;
				if (bufferEst < 0)
					bufferEst = 0;
				buffer_error_sum[j*m_usercount + i] += (float)(quantity - bufferEst) / (float)(quantity + 1 + bufferEst);
				float temp = (float)(quantity - bufferEst) / 3000.0 + (float)buffer_error_sum[j*m_usercount + i] / 3000.0;
				bitrate_list[j*m_usercount + i] += (int)(0.2*temp);
			}
		}
	}
    return 0;
}
int Multilive::optimize_solve(int **thp_down,int  **thp_up){
	cout<<"this is a solve plan"<<endl;
	int *est_up = new int[m_usercount];
	int *est_down = new int[m_usercount];
	//cout<<"init is ok"<<endl;
	for(int i =0;i<m_usercount;i++){
		est_up[i]=estimate(*(thp_up+i));
		est_down[i]=estimate(*(thp_down+i));
		//cout<<*(*(thp_up)+10)<<endl;
	}
	//cout<<"estimate is ok"<<endl;
	for(int i =0;i<m_usercount;i++){
		for(int j =0;j<m_usercount;j++){
			int sum_qoe = 0;
			for (int k = 0; k < m_usercount; k++) {
				sum_qoe +=m_QoE_matrix[k*m_usercount + j];
			}
			//cout<<m_QoE_matrix[0]<<endl;
			if (i != j)
				bitrate_list[i*m_usercount+j]= m_QoE_matrix[i*m_usercount+j]*est_down[j]/sum_qoe;
			if (bitrate_list[i*m_usercount + j] > est_up[i])
				bitrate_list[i*m_usercount + j] = est_up[i];
		}
	}
	//cout<<"caculation is ok"<<endl;
	delete[]est_up;
	delete[]est_down;
	return 0;
}

int * Multilive::stream_sort(int  stream_count, int (*QoE)(int recieverid, int senderid, int bitrate))

{
	cout<<"this is sort"<<endl;
	cout<<stream_count<<endl;
	for (int senderid = 0; senderid < m_usercount; senderid++) {
		//cout<<senderid<<endl;
		float *center = new float[stream_count];
		center[0] = *max_element(bitrate_list + senderid * m_usercount, bitrate_list + senderid*m_usercount+m_usercount);
		center[stream_count - 1] = center[0]/2;
		if(stream_count>2){
		for (int i = 1;i < stream_count - 1; i++) {
			center[i] = i * center[stream_count] / stream_count + (stream_count - i)  * center[0] / stream_count;
		}
		}
		float *last_center = new float[stream_count];
		for (int i = 0; i < stream_count; i++) {
			last_center[i] = 0;
		}
		int *selector = new int[stream_count*m_usercount];
		memset(selector, 0, stream_count*m_usercount * sizeof(int));
		while (last_center[stream_count / 2] / center[stream_count / 2] > 1.2 || last_center[stream_count / 2] / center[stream_count / 2] < 0.8) {
			for (int i = 0; i < m_usercount; i++) {
				int nearest = 0;
				for (int j = 0; j < stream_count; j++) {
					if (abs((*QoE)(i, senderid, bitrate_list[senderid*m_usercount + i]) - (*QoE)(i, senderid, center[j])) < abs((*QoE)(i, senderid, bitrate_list[senderid*m_usercount + i]) - QoE(i, senderid, center[j - 1]))) {
						nearest = j;
					}
				}
				selector[nearest*m_usercount + i] = bitrate_list[senderid*m_usercount + i];
			}
			for (int i = 0; i < stream_count; i++) {
				last_center[i] = center[i];
			}
			for (int i = 0; i < stream_count; i++) {
				int count = 0;
				center[i]=0;
				for (int j = 0; j < m_usercount; j++) {
					if (selector[i*m_usercount + j] != 0) {
						center[i] += selector[i*m_usercount + j];
						count++;
					}
				}
				if (count != 0) {
					center[i] = center[i] / count;
				}
				else
				center[i]=last_center[i];
				
			}
			for(int i =0;i<2;i++){
				//cout<<center[i]<<endl;
			}

			memset(selector, 0, stream_count*m_usercount * sizeof(int));
		}
		for (int i = 0; i < m_usercount; i++) {
			if(i!=senderid){
				int nearest = 0;
				for (int j = 1; j < stream_count; j++) {
					if ((*QoE)(i, senderid, center[j]) > (*QoE)(i, senderid, center[j - 1])) {
						nearest = j;
					}
					user_sort_out[senderid*m_usercount + i] = center[nearest];
			}
			}
			else
			user_sort_out[senderid*m_usercount + i]=100;
		}
		delete[]center;
		delete[]last_center;
		delete[]selector;

	}
	return user_sort_out;
}

Reciever::Reciever(int user)
{
	id = 0;
	count = user;
	buffer = new int[user];
	buffersize = new int[user];
	delay = new int[user];
	for (int i = 0; i < user; i++) {
		buffer[i] = 0;
		buffersize[i] = 0;
		delay[i] = 0;
	}
	
}
Reciever::Reciever()
{
	id = 0;
	count = 3;
	buffer = new int[3];
	buffersize = new int[3];
	delay = new int[3];
	for (int i = 0; i < 3; i++) {
		buffer[i] = 0;
		buffersize[i] = 0;
		delay[i] = 0;
	}

}
Reciever::~Reciever()
{
	delete[]buffer;
	delete[]buffersize;
	delete[]delay;
}
int Reciever::update(int n_id, int *n_buffer,int *n_buffersize,int *n_delay){
	id = n_id;
	for(int i =0;i<count;i++){
		buffer[i] = n_buffer[i];
		buffersize[i] = n_buffersize[i];
		delay[i] = n_delay[i];
	}
	return 0;
}
	
extern "C" void* Mlive_Create_Instance(int usercount,int * QoEmatrix){
	Multilive *s =new Multilive(usercount,QoEmatrix);
	return s;
}
extern "C" void Mlive_Release_Instance(Multilive *s){
	s->~Multilive();
}
extern "C" void Mlive_Optimize_Solve(Multilive *s,int **thp_down,int  **thp_up){
	s->optimize_solve(thp_down,thp_up);
}
extern "C" void Mlive_Buffer_Feedback(Multilive *s,int * buffersize, int ** thp_down, int gap){
	s->buffer_feedback(buffersize,thp_down, gap);
}
extern "C" int* Mlive_Sort_Out(Multilive *s,int  stream_count, int (*QoE)(int recieverid, int senderid, int bitrate)){
	
	return s->stream_sort(stream_count, (*QoE));
}


